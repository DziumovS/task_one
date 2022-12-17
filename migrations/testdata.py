"""
create test data
"""

from yoyo import step


__depends__ = {'tables'}

steps = [
    step("INSERT INTO authors (name, surname, created_at) VALUES ('name1', 'surname1', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('name2', 'surname2', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('name3', 'surname3', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('name4', 'surname4', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('name5', 'surname5', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('name6', 'surname6', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('name7', 'surname7', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('name8', 'surname8', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('name9', 'surname9', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('name10', 'surname10', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('name11', 'surname11', NOW());"),
    step("INSERT INTO authors (name, surname, created_at) VALUES ('name12', 'surname12', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('book name 1', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('book name 2', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('book name 3', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('book name 4', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('book name 5', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('book name 6', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('book name 7', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('book name 8', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('book name 9', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('book name 10', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('book name 11', NOW());"),
    step("INSERT INTO books (name, created_at) VALUES ('book name 12', NOW());"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('1', '1');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('2', '7');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('3', '4');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('3', '5');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('3', '6');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('4', '2');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('4', '3');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('2', '8');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('4', '8');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('3', '11');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('3', '12');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('3', '10');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('2', '10');"),
    step("INSERT INTO author_books (author_id, book_id) VALUES ('1', '11');"),
]
