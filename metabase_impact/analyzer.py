"""SQL query analyzer for detecting table/column references."""

from sqlglot import exp, parse_one
from sqlglot.errors import ParseError


def get_table_column_pairs(query: str) -> set[tuple[str, str]]:
    """
    Extract all (table, column) pairs from a SQL query.

    Resolves aliases to actual table names.

    Args:
        query: SQL query string

    Returns:
        Set of (table_name, column_name) tuples, all lowercase
    """
    try:
        parsed = parse_one(query)
    except ParseError:
        return set()

    # Build alias -> table mapping
    alias_to_table: dict[str, str] = {}
    for table in parsed.find_all(exp.Table):
        table_name = table.name.lower()
        if table.alias:
            alias_to_table[table.alias.lower()] = table_name
        alias_to_table[table_name] = table_name

    # Extract (table, column) pairs
    pairs: set[tuple[str, str]] = set()
    for column in parsed.find_all(exp.Column):
        column_name = column.name.lower()
        table_ref = column.table.lower() if column.table else None

        if table_ref and table_ref in alias_to_table:
            # Qualifier is alias or table name - resolve to real table
            pairs.add((alias_to_table[table_ref], column_name))
        elif table_ref:
            # Qualifier not in our mapping - keep as-is
            pairs.add((table_ref, column_name))
        else:
            # No qualifier - associate with all tables (may cause false positives)
            for table_name in set(alias_to_table.values()):
                pairs.add((table_name, column_name))

    return pairs


def get_tables(query: str) -> set[str]:
    """
    Extract all table names from a SQL query.

    Args:
        query: SQL query string

    Returns:
        Set of table names, all lowercase
    """
    try:
        parsed = parse_one(query)
    except ParseError:
        return set()

    tables: set[str] = set()
    for table in parsed.find_all(exp.Table):
        tables.add(table.name.lower())

    return tables


def references_column(query: str, table: str, column: str) -> bool:
    """
    Check if a SQL query references a specific column from a table.

    Args:
        query: SQL query string
        table: Table name
        column: Column name

    Returns:
        True if the query references the column
    """
    pairs = get_table_column_pairs(query)
    return (table.lower(), column.lower()) in pairs


def references_table(query: str, table: str) -> bool:
    """
    Check if a SQL query references a specific table.

    Args:
        query: SQL query string
        table: Table name

    Returns:
        True if the query references the table
    """
    tables = get_tables(query)
    return table.lower() in tables
