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
