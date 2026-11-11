# Book Catalog MCP Server (hosted)

A FastMCP server that lets Claude manage my book catalog. It runs online on **Prefect Horizon** and stores data in a **Turso** database (SQLite in the cloud). Without Turso settings it falls back to a local `catalog.db` file.

## Local setup

```bash
uv sync
uv run setup_db.py   # creates catalog.db with sample books
uv run server.py     # starts the server
```

## Hosted on Prefect Horizon

1. Set the Turso settings in your shell and create the `books` table online (run once):
   ```bash
   export TURSO_DATABASE_URL="libsql://<your-db>.turso.io"
   export TURSO_AUTH_TOKEN="<your-token>"
   uv run setup_db.py
   ```
2. In Horizon, use the entrypoint `server.py:mcp` and add the same two environment variables.
3. Push to GitHub; Horizon redeploys. Add the Horizon URL to Claude as a custom connector.

## The `books` table

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Assigned automatically |
| `title` | TEXT | Required |
| `author` | TEXT | Required |
| `genre` | TEXT | e.g. Sci-Fi, Memoir |
| `status` | TEXT | Defaults to `want to read` |
| `rating` | INTEGER | 1-5, for books already read |
| `loaned_to` | TEXT | Who borrowed it |

## Tools

| Tool | What it does |
|---|---|
| `search_books` | Search by title, author, or genre. Empty query lists every book. |
| `add_book` | Add a new book. |
| `update_status` | Change a book's reading status, and optionally rate it 1-5. |
| `delete_book` | Permanently delete a book. |

Statuses: `want to read`, `reading`, `read`.
