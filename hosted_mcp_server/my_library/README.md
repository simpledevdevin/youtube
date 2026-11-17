# Book Catalog MCP Server (hosted)

A FastMCP server that lets Claude manage a personal book catalog. It runs online on **Prefect Horizon** and stores its data in a **Turso** database (SQLite in the cloud). Without Turso settings it falls back to a local `catalog.db` file, so you can try it on your own computer first.

## What you need

- [uv](https://docs.astral.sh/uv/) (installs Python and the dependencies for you)
- A free [Turso](https://turso.tech) account
- A Prefect Horizon account
- A GitHub account (Horizon deploys from your GitHub repo)
- Claude, to connect to the server

## 1. Run it locally (optional)

From this folder:

```bash
uv sync              # install dependencies
uv run setup_db.py   # create catalog.db with 7 sample books
uv run server.py     # start the server
```

## 2. Set up the Turso database

You need two values from Turso: the **database URL** and an **auth token**.

### Create the database

Pick **one** of these.

**Option A: create an empty database and let the script fill it (simplest)**

1. In the Turso dashboard, create a new database, or with the [Turso CLI](https://docs.turso.tech/cli/introduction):
   ```bash
   turso auth login
   turso db create book-catalog
   ```
2. Get the URL and make a token (or copy both from the dashboard):
   ```bash
   turso db show book-catalog --url      # libsql://book-catalog-<you>.turso.io
   turso db tokens create book-catalog
   ```
3. Set them in your terminal and run the setup script. It creates the `books` table online and adds the sample books:
   ```bash
   export TURSO_DATABASE_URL="libsql://<your-db>.turso.io"
   export TURSO_AUTH_TOKEN="<your-token>"
   uv run setup_db.py
   ```
   It should end with `Using Turso`. If it prints a file path, the variables weren't set.

**Option B: upload your local `catalog.db`**

Turso only accepts SQLite files in WAL mode. Otherwise you get
`Protocol error: upload works only for DBs with journal_mode=WAL`. Switch the file first:

```bash
sqlite3 catalog.db "PRAGMA journal_mode=WAL; PRAGMA wal_checkpoint(TRUNCATE);"
```

It should print `wal`. Then upload `catalog.db` when you create the database in the Turso dashboard (only the `.db` file; ignore `catalog.db-wal` and `catalog.db-shm`). Get the URL and token as in Option A, step 2.

## 3. Push the code to GitHub

Horizon deploys from GitHub, so the code has to be pushed first. The `.gitignore` keeps the `.db` files, `.venv` and `.env` out of the repo.

```bash
git add .
git status    # check that no .db, .venv or .env files are listed
git commit -m "Add hosted MCP server"
git push
```

## 4. Deploy on Prefect Horizon

1. Create a new server in Horizon and connect it to your GitHub repo and branch.
2. Set the **entrypoint** to `file path:server object`, relative to the **root of the repo**:
   - If this folder is the repo root: `server.py:mcp`
   - If it's inside a bigger repo, include the folders, for example:
     `hosted_mcp_server/my_library/server.py:mcp`
3. Add two **environment variables**, with the values from Turso:

   | Name | Value |
   |---|---|
   | `TURSO_DATABASE_URL` | `libsql://<your-db>.turso.io` |
   | `TURSO_AUTH_TOKEN` | your Turso token |

4. Make sure **FastMCP Gateway Authentication** is **enabled**. With it on, only people who are logged in and are members of your Horizon organization can connect, even if someone else knows the URL.
5. Deploy. Every push to GitHub after that redeploys automatically.
6. Check the deploy logs. If you see `ModuleNotFoundError: libsql`, Horizon didn't pick up `pyproject.toml`. The easiest fix is to put this folder in its own repo and use `server.py:mcp` as the entrypoint.

## 5. Connect it to Claude

1. Copy your server's URL from Horizon.
2. In Claude, go to **Settings → Connectors → Add custom connector** and paste the URL.
3. Log in when asked (that's the Gateway Authentication).
4. Try it: *"Search my books"* should list the sample books.

If Claude says `no such table: books`, the environment variables point at a database without the table. Run `setup_db.py` against it (step 2, Option A).

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

## Keeping it safe

- **Never commit your Turso token.** Keep it only in Horizon's environment variables and your terminal. If it leaks (including on screen in a video), revoke it in Turso and create a new one.
- **Keep Gateway Authentication on**, and only add people you trust to your Horizon organization.
- **Turn on two-factor login** for GitHub, Horizon and Turso. Those logins are the way in to your server and data.
- **Watch for prompt injection.** Claude reads whatever the tools return, so text planted in the database could try to steer Claude toward your other connectors (email, files, social accounts). Keep approval prompts on for actions that send, post or share.
