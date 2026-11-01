"""A simple FastMCP server for a personal book catalog.

Install:  uv sync  (or: pip install fastmcp)
Run:      uv run server.py
"""

import sqlite3  # Built-in Python module for working with SQLite databases
from pathlib import Path  # Builds the path to the database file
from typing import Literal  # Limits a value to a fixed set of options
from fastmcp import FastMCP  # The library that turns Python functions into an MCP server

# The SQLite database created by setup_db.py
DB_PATH = Path(__file__).parent / "catalog.db"

# Create the MCP server. This name is what shows up in Claude.
mcp = FastMCP("Book Catalog")

# The only allowed reading statuses. Claude can't send anything else.
Status = Literal["want to read", "reading", "read"]


def get_db():
    """Open the database and return rows as dictionaries."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --- Tools: functions Claude can call on its own ---
# @mcp.tool turns a regular Python function into an MCP tool.
# Claude reads the function name, parameters, and docstring to decide when to use it.


@mcp.tool
def search_books(query: str = "") -> list[dict]:
    """Search my book catalog by title, author, or genre.

    Leave query empty to list every book. Use this to find a book's id.
    """
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?",
            (f"%{query}%",) * 3,
        ).fetchall()
    return [dict(row) for row in rows]


@mcp.tool
def add_book(
    title: str,
    author: str,
    genre: str | None = None,
    status: Status = "want to read",
    rating: int | None = None,
) -> dict:
    """Add a new book to the catalog. Rating is 1-5 and only for books already read."""
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO books (title, author, genre, status, rating) "
            "VALUES (?, ?, ?, ?, ?)",
            (title, author, genre, status, rating),
        )
        new_id = cur.lastrowid
    return {"message": f"Added '{title}'", "id": new_id}


@mcp.tool
def update_status(book_id: int, status: Status, rating: int | None = None) -> dict:
    """Change a book's reading status, and optionally rate it 1-5."""
    with get_db() as conn:
        cur = conn.execute(
            "UPDATE books SET status = ?, rating = ? WHERE id = ?",
            (status, rating, book_id),
        )
    if cur.rowcount == 0:
        return {"message": f"No book found with id {book_id}."}
    return {"message": f"Updated book {book_id} to '{status}'"}


@mcp.tool
def delete_book(book_id: int) -> dict:
    """Permanently delete a book from the catalog by its id."""
    with get_db() as conn:
        cur = conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    if cur.rowcount == 0:
        return {"message": f"No book found with id {book_id}."}
    return {"message": f"Deleted book {book_id}"}


# Start the server when this file is run directly
if __name__ == "__main__":
    mcp.run()
