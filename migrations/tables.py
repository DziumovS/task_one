"""
create tables with columns
"""

from yoyo import step


__depends__ = {}

steps = [step("""CREATE TABLE IF NOT EXISTS authors(
    id serial PRIMARY KEY,
    name text NOT NULL,
    surname text NOT NULL,
    created_at timestamptz,
    updated_at timestamptz);
    CREATE TABLE IF NOT EXISTS books(
    id serial PRIMARY KEY,
    name text UNIQUE NOT NULL,
    created_at timestamptz,
    updated_at timestamptz);
    CREATE TABLE IF NOT EXISTS author_books(
    author_id int REFERENCES authors (id) ON DELETE CASCADE,
    book_id int REFERENCES books (id) ON DELETE CASCADE);""")]
