# metabase-impact

A CLI tool that helps data teams prevent breaking Metabase questions when making database schema changes.

## Problem

When engineers drop/rename columns or tables, they often break Metabase reports without realizing it. This tool scans all Metabase questions (cards) to find which ones will be affected BEFORE the schema change is deployed.

## MVP Scope

- CLI that takes `--metabase-url`, `--api-key`, and `--drop-column table.column` flags
- Fetches all cards from Metabase API (GET /api/card)
- Uses sqlglot for SQL parsing to find cards whose queries reference the dropped column/table
- Outputs a list of affected cards with links to them in Metabase
- Clean, professional code (public GitHub repo)
- Type hints, docstrings, basic error handling
- Uses click for CLI, rich for output formatting, requests for API calls

## Technical Decisions

- Uses sqlglot for SQL parsing (handles aliases, complex queries)
- Only supports native SQL queries (not MBQL visual queries)
- Open source (MIT license)
- Python 3.10+
