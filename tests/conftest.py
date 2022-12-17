import pytest
import lib_app
from settings.main import connection


@pytest.fixture()
def app():
    app = lib_app.app
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def create_tables():
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS authors(
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
                    book_id int REFERENCES books (id) ON DELETE CASCADE);
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_authors_name_surname ON authors (name, surname);
                    INSERT INTO authors (name, surname, created_at) VALUES ('name1', 'surname1', NOW());
                    INSERT INTO authors (name, surname, created_at) VALUES ('name2', 'surname2', NOW());
                    INSERT INTO authors (name, surname, created_at) VALUES ('name3', 'surname3', NOW());
                    INSERT INTO authors (name, surname, created_at) VALUES ('name4', 'surname4', NOW());
                    INSERT INTO authors (name, surname, created_at) VALUES ('name5', 'surname5', NOW());
                    INSERT INTO authors (name, surname, created_at) VALUES ('name6', 'surname6', NOW());
                    INSERT INTO authors (name, surname, created_at) VALUES ('name7', 'surname7', NOW());
                    INSERT INTO authors (name, surname, created_at) VALUES ('name8', 'surname8', NOW());
                    INSERT INTO authors (name, surname, created_at) VALUES ('name9', 'surname9', NOW());
                    INSERT INTO authors (name, surname, created_at) VALUES ('name10', 'surname10', NOW());
                    INSERT INTO authors (name, surname, created_at) VALUES ('name11', 'surname11', NOW());
                    INSERT INTO authors (name, surname, created_at) VALUES ('name12', 'surname12', NOW());
                    INSERT INTO books (name, created_at) VALUES ('book name 1', NOW());
                    INSERT INTO books (name, created_at) VALUES ('book name 2', NOW());
                    INSERT INTO books (name, created_at) VALUES ('book name 3', NOW());
                    INSERT INTO books (name, created_at) VALUES ('book name 4', NOW());
                    INSERT INTO books (name, created_at) VALUES ('book name 5', NOW());
                    INSERT INTO books (name, created_at) VALUES ('book name 6', NOW());
                    INSERT INTO books (name, created_at) VALUES ('book name 7', NOW());
                    INSERT INTO books (name, created_at) VALUES ('book name 8', NOW());
                    INSERT INTO books (name, created_at) VALUES ('book name 9', NOW());
                    INSERT INTO books (name, created_at) VALUES ('book name 10', NOW());
                    INSERT INTO books (name, created_at) VALUES ('book name 11', NOW());
                    INSERT INTO books (name, created_at) VALUES ('book name 12', NOW());
                    INSERT INTO author_books (author_id, book_id) VALUES ('1', '1');
                    INSERT INTO author_books (author_id, book_id) VALUES ('2', '7');
                    INSERT INTO author_books (author_id, book_id) VALUES ('3', '4');
                    INSERT INTO author_books (author_id, book_id) VALUES ('3', '5');
                    INSERT INTO author_books (author_id, book_id) VALUES ('3', '6');
                    INSERT INTO author_books (author_id, book_id) VALUES ('4', '2');
                    INSERT INTO author_books (author_id, book_id) VALUES ('4', '3');
                    INSERT INTO author_books (author_id, book_id) VALUES ('2', '8');
                    INSERT INTO author_books (author_id, book_id) VALUES ('4', '8');
                    INSERT INTO author_books (author_id, book_id) VALUES ('3', '11');
                    INSERT INTO author_books (author_id, book_id) VALUES ('3', '12');
                    INSERT INTO author_books (author_id, book_id) VALUES ('3', '10');
                    INSERT INTO author_books (author_id, book_id) VALUES ('2', '10');
                    INSERT INTO author_books (author_id, book_id) VALUES ('1', '11');""")
    connection.commit()


@pytest.fixture(autouse=True)
def drop_tables():
    yield
    cursor = connection.cursor()
    cursor.execute("""DROP TABLE IF EXISTS author_books, authors, books CASCADE;""")
    connection.commit()
