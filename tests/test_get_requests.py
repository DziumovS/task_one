import pytest


class TestGETRequests:
    @pytest.mark.parametrize("_id", [11, 7, 'cat', 777])
    def test_author_get_request(self, client, create_tables, _id):
        url = "api/author/" + str(_id)
        response = client.get(url)
        if _id == 11:
            assert len(response.json['author_books']) == 2
        elif _id == 7:
            assert not response.json['author_books']
        elif _id == 11 or _id == 7:
            assert response.status_code == 200
            assert response.json
            assert response.json['author_info']
            assert response.json['author_info']['name']
            assert response.json['author_info']['surname']
            assert response.json['author_info']['created_at']
            assert response.json['author_info']['id'] == _id
        else:
            assert response.status_code == 404

    @pytest.mark.parametrize("_id", [11, 9, 'cat', 777])
    def test_book_get_request(self, client, create_tables, _id):
        url = "api/book/" + str(_id)
        response = client.get(url)
        if _id == 11:
            assert len(response.json['authors_of_book']) == 2
        elif _id == 9:
            assert not response.json['authors_of_book']
        elif _id == 11 or _id == 9:
            assert response.status_code == 200
            assert response.json
            assert response.json['book_info']
            assert response.json['book_info']['name']
            assert response.json['book_info']['created_at']
            assert response.json['book_info']['id'] == _id
        else:
            assert response.status_code == 404

    @pytest.mark.parametrize("page, per_page", [('', ''),
                                                ('?page=2', ''),
                                                ('?page=2', '&per_page=2'),
                                                ('', '?per_page=20')])
    def test_author_get_request_with_pagination(self, client, create_tables, page, per_page):
        url = "api/author" + page + per_page
        response = client.get(url)
        assert response.status_code == 200
        assert response.json['data_info']
        assert response.json['pagination']
        if not per_page:
            assert len(response.json['data_info']) == 5
        elif per_page == '&per_page=2':
            assert len(response.json['data_info']) == 2
        elif per_page == '&per_page=20':
            assert len(response.json['data_info']) == 10

    @pytest.mark.parametrize("page, per_page", [('', ''),
                                                ('?page=2', ''),
                                                ('?page=2', '&per_page=2'),
                                                ('', '?per_page=20')])
    def test_book_get_request_with_pagination(self, client, create_tables, page, per_page):
        url = "api/book" + page + per_page
        response = client.get(url)
        assert response.status_code == 200
        assert response.json['data_info']
        assert response.json['pagination']
        if not per_page:
            assert len(response.json['data_info']) == 5
        elif per_page == '&per_page=2':
            assert len(response.json['data_info']) == 2
        elif per_page == '&per_page=20':
            assert len(response.json['data_info']) == 10

    @pytest.mark.parametrize("_id", [11, 9, 'cat', 777])
    def test_author_books_get_request(self, client, create_tables, _id):
        url = "api/author/books/" + str(_id)
        response = client.get(url)
        if _id == 11:
            assert len(response.json['data_info']) == 2
        elif _id == 9:
            assert not response.json['data_info']
        elif _id == 11 or _id == 9:
            assert response.status_code == 200
            assert response.json
            assert response.json['pagination']
            assert response.json['pagination']['books_count']
            assert response.json['pagination']['current_page']
            assert response.json['pagination']['total_pages']
        else:
            assert response.status_code == 404

    @pytest.mark.parametrize("_id, page, per_page", [(11, '', ''),
                                                     (11, '?page=2', ''),
                                                     (11, '?page=2', '&per_page=2'),
                                                     (11, '', '?per_page=20'),
                                                     (9, '', ''),
                                                     (9, '?page=2', ''),
                                                     (9, '?page=2', '&per_page=2'),
                                                     (9, '', '?per_page=20')])
    def test_author_books_get_request_with_pagination(self, client, create_tables, _id, page, per_page):
        url = "api/author/books/" + str(_id) + page + per_page
        response = client.get(url)
        assert response.status_code == 200
        assert response.json['pagination']
        if _id == 11:
            if not page and not per_page:
                assert response.json['data_info']
                assert len(response.json['data_info']) == 2
            elif page and not per_page or page and per_page:
                assert not response.json['data_info']
            elif not page and per_page:
                assert response.json['data_info']
                assert len(response.json['data_info']) == 2
        elif _id == 9:
            assert not response.json['data_info']
            if not page and not per_page or page and not per_page or page and per_page or not page and per_page:
                assert not response.json['data_info']
