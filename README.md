## Небольшое API-приложение библиотеки

### Вводные
1) Формат передачи данных от приложения и к нему - JSON


2) В качестве инфраструктуры:

   2.1) postgres в docker

   2.2) подключение к базе через psycopg2

   2.3) для миграций используется yoyo-migrations

   2.4) используемый тип таблиц: "many-to-many"

   2.5) в качестве фреймворка Flask


3) Ручки

	#### /api/author
	- `POST`: создает нового автора
	- `GET`: возвращает список авторов (с пагинацией)

	#### /api/author/:id
	- `GET`: позволяет получить полную информацию об авторе
	- `PUT`: позволяет обновить данные по автору (в том числе редактировать список его книг)
	- `DELETE`: удаляет автора и все связанные с ним книги (если автором книги является только он, в противном случае возвращает 400 ответ)
		
	#### /api/author/books/:id
	- `GET`: возвращает список книг указанного автора (с пагинацией)

	#### /api/book
	- `POST`: позволяет создать новую книгу, с уникальным названием для каждой, у книги может быть несколько авторов
	- `GET`: возвращает список книг (с пагинацией)

	#### /api/book/:id
	- `GET`: позволяет получить полную информацию о книге, включая её авторов
	- `PUT`: позволяет обновить данные о книге (в том числе добавлять / исключать авторов)
	- `DELETE`: удаляет книгу и связанную с ней информацию

---

## Small API application of the library

### Introductions
1) The format of data transfer from and to the application is JSON


2) As infrastructure:

   2.1) postgres in docker

   2.2) psycopg2 connection to the database

   2.3) yoyo-migrations is used for migrations

   2.4) the type of tables used: "many-to-many"

   2.5) Flask as framework


3) Handles

	#### /api/author
	- `POST`: creates a new author
	- `GET`: returns a list of authors (with pagination)

	#### /api/author/:id
	- `GET`: allows you to get the full information about an author
	- `PUT`: allows you to update an author's details (including editing his book list)
	- `DELETE`: deletes the author and all books related to him (if only he is the author, otherwise it returns 400 response)
		
	#### /api/author/books/:id
	- `GET`: returns a list of books by the specified author (with pagination)

	#### /api/books
	- `POST`: allows you to create a new book, with a unique title for each, the book can have multiple authors
	- `GET`: returns list of books (with pagination)

	#### /api/book/:id
	- `GET`: allows you to get complete information about a book, including its authors
	- `PUT`: allows you to update data about a book (including adding/removing authors)
	- `DELETE`: deletes the book and its related information
