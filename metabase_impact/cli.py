"""CLI for metabase-impact."""

import click
from rich.console import Console
from rich.table import Table

from metabase_impact.analyzer import references_column, references_table
from metabase_impact.client import MetabaseClient, MetabaseAPIError


@click.command()
@click.option("--metabase-url", required=True, help="Metabase instance URL")
@click.option("--api-key", required=True, help="Metabase API key")
@click.option(
    "--drop-column",
    multiple=True,
    help="Column to drop (format: table.column)",
)
@click.option(
    "--drop-table",
    multiple=True,
    help="Table to drop",
)
def main(metabase_url: str, api_key: str, drop_column: tuple[str, ...], drop_table: tuple[str, ...]) -> None:
    """Find Metabase questions affected by schema changes.

    Example: metabase-impact --metabase-url http://localhost:3000 --api-key "mb_xxx" --drop-column orders.user_id
    """
    console = Console()

    if not drop_column and not drop_table:
        console.print("[red]Error:[/red] Specify at least one --drop-column or --drop-table")
        raise SystemExit(1)

    # Parse column specs
    columns: list[tuple[str, str]] = []
    for spec in drop_column:
        if "." not in spec:
            console.print(f"[red]Error:[/red] Invalid column format '{spec}'. Use table.column")
            raise SystemExit(1)
        table, column = spec.split(".", 1)
        columns.append((table, column))

    # Fetch cards
    try:
        client = MetabaseClient(metabase_url, api_key)
        cards = client.get_cards()
    except MetabaseAPIError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    if not cards:
        console.print("[yellow]No native SQL questions found in Metabase[/yellow]")
        return

    # Find affected cards
    affected: list[tuple[str, int, str, list[str]]] = []
    for card in cards:
        reasons: list[str] = []
        for table, column in columns:
            if references_column(card.query, table, column):
                reasons.append(f"{table}.{column}")
        for table in drop_table:
            if references_table(card.query, table):
                reasons.append(f"table {table}")
        if reasons:
            affected.append((card.name, card.id, f"{metabase_url}/question/{card.id}", reasons))

    # Output results
    if not affected:
        console.print("[green]No questions affected by these changes[/green]")
        return

    output_table = Table(title="Affected Questions")
    output_table.add_column("Question", style="cyan")
    output_table.add_column("ID", style="dim")
    output_table.add_column("Reason", style="yellow")
    output_table.add_column("Link", style="blue")

    for name, card_id, link, reasons in affected:
        output_table.add_row(name, str(card_id), ", ".join(reasons), link)

    console.print(output_table)
    console.print(f"\n[red]Found {len(affected)} affected question(s)[/red]")


if __name__ == "__main__":
    main()
