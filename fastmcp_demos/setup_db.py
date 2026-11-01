"""Creates catalog.db with a books table and some sample data.

No packages to install: sqlite3 and pathlib come with Python.

Run once before starting the server, from this folder:
    uv run setup_db.py
    (or without uv: python setup_db.py)
"""

import sqlite3
from pathlib import Path

# The database file lives next to this script
DB_PATH = Path(__file__).parent / "catalog.db"

# Connect to the database (creates the file if it doesn't exist)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Create the books table
cur.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT,
    status TEXT DEFAULT 'want to read',
    rating INTEGER,
    loaned_to TEXT
)
""")

# Sample books to start with
books = [
    ("Dune", "Frank Herbert", "Sci-Fi", "want to read", None, None),
    ("The Lord of the Rings: The Fellowship of the Ring", "J.R.R. Tolkien", "Fantasy", "read", 5, None),
    ("The Big Short", "Michael Lewis", "Finance", "reading", None, None),
    ("Project Hail Mary", "Andy Weir", "Sci-Fi", "want to read", None, None),
    ("Educated", "Tara Westover", "Memoir", "read", 4, None),
    ("The Glass Castle", "Jeannette Walls", "Memoir", "read", 5, None),
    ("War and Peace", "Leo Tolstoy", "Classic", "want to read", None, None),
]

# Only add the sample books if the table is empty, so existing data is never touched
count = cur.execute("SELECT COUNT(*) FROM books").fetchone()[0]
if count == 0:
    cur.executemany(
        "INSERT INTO books (title, author, genre, status, rating, loaned_to) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        books,
    )
    print(f"Added {len(books)} sample books.")
else:
    print(f"Table already has {count} books. Nothing changed.")

# Save changes and close the connection
conn.commit()
conn.close()
print(f"Database is at: {DB_PATH}")
