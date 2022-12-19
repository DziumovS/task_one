import pytest


class TestPOSTRequests:
    @pytest.mark.parametrize("name_key, surname_key, name_value, surname_value", [
        ('name', '', 'Testname', ''),
        ('', 'surname', '', 'Testsurname'),
        ('', '', '', ''),
        ('name', 'surname', 'name1', 'surname1'),
        ('name', 'surname', 'testname', 'testsurname')])
    def test_author_post_request(self, client, create_tables, name_key, surname_key, name_value, surname_value):
        url = "api/author"
        data = {
            name_key: name_value,
            surname_key: surname_value
        }
        check_authors_count = client.get('api/author')
        response = client.post(url, json=data)
        test_author_id_must_be = check_authors_count.json['pagination']['authors_count'] + 1
        if name_value == 'testname' and surname_value == 'testsurname':
            assert response.status_code == 201
            assert response.json
            assert response.json['added_author']
            assert response.json['added_author']['created_at']
            assert response.json['added_author']['id']
            assert response.json['added_author']['id'] == test_author_id_must_be
            assert response.json['added_author']['name']
            assert response.json['added_author']['name'] == name_value.title()
            assert response.json['added_author']['surname']
            assert response.json['added_author']['surname'] == surname_value.title()
        elif name_value == 'name1' and surname_value == 'surname1':
            assert response.status_code == 404
        else:
            assert response.status_code == 400

    @pytest.mark.parametrize("name_key, authors_id, name_value, authors_id_value", [
        ('name', '', 'Testname', ''),
        ('', 'authors_id', '', 'Testsurname'),
        ('', 'authors_id', '', []),
        ('', '', '', ''),
        ('name', 'authors_id', 'book name 1', [1, 2]),
        ('name', 'authors_id', 'Testname', [1, 2, 12])])
    def test_book_post_request(self, client, create_tables, name_key, authors_id, name_value, authors_id_value):
        url = "api/book"
        data = {
            name_key: name_value,
            authors_id: authors_id_value
        }
        check_books_count = client.get('api/book')
        response = client.post(url, json=data)
        test_book_id_must_be = check_books_count.json['pagination']['books_count'] + 1
        if name_value == 'Testname' and authors_id_value == [1, 2, 12]:
            assert response.status_code == 201
            assert response.json
            assert response.json['book_info']
            assert response.json['book_info']['created_at']
            assert response.json['book_info']['id']
            assert response.json['book_info']['id'] == test_book_id_must_be
            assert response.json['book_info']['name']
            assert response.json['book_info']['name'] == name_value
            assert response.json['authors_of_book']
            temp = [int(author_id) for author_id in response.json['authors_of_book']]
            for i in range(len(authors_id_value)):
                assert authors_id_value[i] == int(temp[i])
            for a_id in authors_id_value:
                response_author_check = client.get('api/author/' + str(a_id))
                assert response_author_check.status_code == 200
                assert response_author_check.json['author_info']['updated_at'] is not None
                assert str(test_book_id_must_be) in response_author_check.json['author_books']
        elif name_value == 'book name 1' and authors_id_value == [1, 2]:
            assert response.status_code == 400
        else:
            assert response.status_code == 404
