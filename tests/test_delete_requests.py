import pytest


class TestDELETERequests:
    @pytest.mark.parametrize("_id", [11, 7, 'cat', 777])
    def test_author_delete_request(self, client, create_tables, _id):
        url_author = "api/author/" + str(_id)
        response_get = client.get(url_author)
        if _id == 11 or _id == 7:
            assert response_get.status_code == 200
            author_books = response_get.json['author_books']
            list_of_authors_book = list()
            if author_books:
                for book in author_books.keys():
                    url_book_of_author = "api/book/" + book
                    response_get_book_of_author = client.get(url_book_of_author)
                    this_author_book = response_get_book_of_author.json['authors_of_book']
                    if len(this_author_book) == 1:
                        list_of_authors_book.append(book)
            response_delete = client.delete(url_author)
            assert response_delete.status_code == 200
            assert response_delete.json
            assert response_delete.json['deleted_author']
            assert response_delete.json['deleted_author']['id'] == _id
            if list_of_authors_book:
                for book in list_of_authors_book:
                    url_book_of_author = "api/book/" + book
                    response_get_book_of_author = client.get(url_book_of_author)
                    assert response_get_book_of_author.status_code == 404
        else:
            assert response_get.status_code == 404

    @pytest.mark.parametrize("_id", [11, 7, 'cat', 777])
    def test_book_delete_request(self, client, create_tables, _id):
        url_book = "api/book/" + str(_id)
        response_get = client.get(url_book)
        if _id == 11 or _id == 7:
            assert response_get.status_code == 200
            response_delete = client.delete(url_book)
            assert response_delete.status_code == 200
            assert response_delete.json
            assert response_delete.json['deleted_book']
            assert response_delete.json['deleted_book']['id'] == _id
        else:
            assert response_get.status_code == 404
