"""
create tables with columns
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """CREATE TABLE authors(
            id serial PRIMARY KEY,
            name text NOT NULL,
            surname text NOT NULL,
            created_at timestamptz,
            updated_at timestamptz);
        """),
    step(
        """CREATE TABLE books(
            id serial PRIMARY KEY,
            name text UNIQUE NOT NULL,
            created_at timestamptz,
            updated_at timestamptz);
        """),
    step(
        """CREATE TABLE author_books(
            author_id int REFERENCES authors (id) ON DELETE CASCADE,
            book_id int REFERENCES books (id) ON DELETE CASCADE);
        """),
    step(
        """CREATE UNIQUE INDEX idx_authors_name_surname ON authors (name, surname);
        """)
]
