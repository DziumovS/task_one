"""
create test data
"""

from yoyo import step

__depends__ = {'tables'}

steps = [
    step("INSERT INTO authors (name, surname, created_at) VALUES ('Джоан', 'Роулинг', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('Анджей', 'Сапковский', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('Стефани', 'Майер', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('Джон', 'Толкин', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('Гарри Поттер', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('Властелин колец', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('Хоббит', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('Сумерки', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('Новолуние', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('Химик', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('Ведьмак', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('Книга с двумя авторами', NOW());"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('1', '1');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('2', '7');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('3', '4');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('3', '5');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('3', '6');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('4', '2');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('4', '3');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('2', '8');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('4', '8');"),
]
