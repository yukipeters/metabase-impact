# metabase-impact

Find which Metabase questions will break when you change your database schema.

## The Problem

When engineers drop or rename columns/tables, they often break Metabase questions without realizing it. This tool scans all native SQL questions to find which ones will be affected **before** the schema change is deployed.

## Installation

```bash
pip install git+https://github.com/yukipeters/metabase-impact.git
```

## Usage

```bash
# Check impact of dropping a column
metabase-impact \
  --metabase-url http://localhost:3000 \
  --api-key "mb_xxx" \
  --drop-column orders.user_id

# Check impact of dropping a table
metabase-impact \
  --metabase-url http://localhost:3000 \
  --api-key "mb_xxx" \
  --drop-table users

# Check multiple changes at once
metabase-impact \
  --metabase-url http://localhost:3000 \
  --api-key "mb_xxx" \
  --drop-column orders.user_id \
  --drop-column orders.product_id \
  --drop-table users
```

## Output

```
Affected Questions

Question     ID   Reason            Link
All Orders   38   orders.user_id    http://localhost:3000/question/38

Found 1 affected question(s)
```

## Getting a Metabase API Key

1. Go to Metabase settings (gear icon)
2. Click "Admin settings"
3. Go to "API Keys" under Authentication
4. Create a new API key

## Limitations

- Only analyzes native SQL questions (not GUI/MBQL questions)
- SQL parsing handles most cases including aliases, but complex CTEs or dynamic SQL may not be fully supported

## License

MIT
