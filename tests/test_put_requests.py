import pytest


class TestPUTRequests:
    @pytest.mark.parametrize("""_id, name_key, name_value, surname_key, surname_value, join_book_key, join_book_value,
                             split_book_key, split_book_value""", [
        (77, '', '', '', '', '', '', '', ''),
        ('cat', '', '', '', '', '', '', '', ''),
        (4, 'new_name', 'name1', 'new_surname', 'surname1', 'join_book_id', [2, 3, 8], 'split_book_id', ''),
        (4, 'new_name', 'name1', 'new_surname', 'surname1', 'join_book_id', [2, 3], 'split_book_id', ''),
        (4, 'new_name', 'name1', 'new_surname', 'surname1', 'join_book_id', [2], 'split_book_id', ''),
        (4, 'new_name', 'name1', 'new_surname', 'surname1', 'join_book_id', [1, 2], 'split_book_id', ''),
        (4, 'new_name', 'name1', 'new_surname', 'surname1', 'join_book_id', '', 'split_book_id', [10]),
        (4, 'new_name', 'Testname', 'new_surname', 'Testsurname', 'join_book_id', [1], 'split_book_id', [77]),
        (3, 'new_name', 'Testname', 'new_surname', 'Testsurname', 'join_book_id', [1, 2, 12], 'split_book_id',
         [4, 5, 6, 10, 11]),
        (10, 'new_name', 'Testname', 'new_surname', 'Testsurname', 'join_book_id', [4, 5, 12], 'split_book_id', [])])
    def test_author_put_request(self, client, create_tables, _id, name_key, name_value, surname_key, surname_value,
                                join_book_key, join_book_value, split_book_key, split_book_value):
        url = "api/author/" + str(_id)
        data = {
            name_key: name_value,
            surname_key: surname_value,
            join_book_key: join_book_value,
            split_book_key: split_book_value
        }
        books_response = client.get(url)
        response = client.put(url, json=data)
        if _id == 4:
            assert response.status_code == 403
        elif _id == 77 or _id == 'cat':
            assert response.status_code == 404
        else:
            author_books_check_at_the_start = [int(book_id) for book_id in books_response.json['author_books']]
            assert response.status_code == 200
            assert response.json
            assert response.json['author_info']
            assert response.json['author_info']['created_at']
            assert response.json['author_info']['id']
            assert response.json['author_info']['name']
            assert response.json['author_info']['name'] == name_value.title()
            assert response.json['author_info']['surname']
            assert response.json['author_info']['surname'] == surname_value.title()
            assert response.json['author_info']['updated_at']
            assert response.json['author_info']['updated_at'] is not None
            for added_book in join_book_value:
                assert str(added_book) in response.json['author_books']
                author_books_check_at_the_start.append(added_book)
            for removed_book in split_book_value:
                assert str(removed_book) not in response.json['author_books']
                author_books_check_at_the_start.remove(removed_book)
            author_books_count_at_the_end = [int(book_id) for book_id in response.json['author_books']]
            assert author_books_check_at_the_start == author_books_count_at_the_end

    @pytest.mark.parametrize("""_id, name_key, name_value, join_author_key, join_author_value,
                             split_author_key, split_author_value""", [
        (77, '', '', '', '', '', ''),
        ('cat', '', '', '', '', '', ''),
        (8, 'new_name', '', 'join_author_id', [2, 4], 'split_author_id', ''),
        (8, 'new_name', '', 'join_author_id', [2], 'split_author_id', ''),
        (8, 'new_name', '', 'join_author_id', [2, 3], 'split_author_id', ''),
        (8, 'new_name', '', 'join_author_id', '', 'split_author_id', [3]),
        (8, 'new_name', 'Testname', 'join_author_id', [1], 'split_author_id', [77]),
        (8, 'new_name', 'book name 1', 'join_author_id', '', 'split_author_id', [3]),
        (2, 'new_name', 'Testname', 'join_author_id', [9, 10, 11, 12], 'split_author_id', [4]),
        (12, 'new_name', 'Testname', 'join_author_id', [5, 6, 7, 8], 'split_author_id', [11])])
    def test_book_put_request(self, client, create_tables, _id, name_key, name_value, join_author_key,
                              join_author_value, split_author_key, split_author_value):
        url = "api/book/" + str(_id)
        data = {
            name_key: name_value,
            join_author_key: join_author_value,
            split_author_key: split_author_value
        }
        authors_response = client.get(url)
        response = client.put(url, json=data)
        if _id == 8:
            if name_value == 'book name 1':
                assert response.status_code == 400
            else:
                assert response.status_code == 403
        elif _id == 77 or _id == 'cat':
            assert response.status_code == 404
        else:
            book_authors_check_at_the_start = [int(author_id) for author_id in authors_response.json['authors_of_book']]
            assert response.status_code == 200
            assert response.json
            assert response.json['book_info']
            assert response.json['book_info']['created_at']
            assert response.json['book_info']['id']
            assert response.json['book_info']['name']
            assert response.json['book_info']['name'] == name_value
            assert response.json['book_info']['updated_at']
            assert response.json['book_info']['updated_at'] is not None
            for added_author in join_author_value:
                assert str(added_author) in response.json['authors_of_book']
                book_authors_check_at_the_start.append(added_author)
            for removed_author in split_author_value:
                assert str(removed_author) not in response.json['authors_of_book']
                book_authors_check_at_the_start.remove(removed_author)
            book_authors_check_at_the_end = [int(book_id) for book_id in response.json['authors_of_book']]
            assert book_authors_check_at_the_start == book_authors_check_at_the_end
