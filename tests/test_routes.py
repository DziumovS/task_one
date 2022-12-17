import pytest


class TestRoutesWithGETMethod:

    def test_post(self, client):
        url = "api/author"
        data = {
            "name": "Name56",
            "surname": "Surname56"
        }
        response = client.post(url, json=data)
        assert response.status_code == 201

    # @pytest.mark.parametrize("_id, page, per_page", [('', '', ''),
    #                                                  ('', '?page=2', ''),
    #                                                  ('', '?page=2', '&per_page=2'),
    #                                                  ('', '', '?per_page=2'),
    #                                                  ('', '', '?per_page=20')])
    # def test_author(self, client, _id, page, per_page):
    #     url = "api/author" + _id + page + per_page
    #     response = client.get(url)
    #     assert response.status_code == 200

    # @pytest.mark.parametrize("_id, page, per_page", [('1', '', ''),
    #                                                  ('1', '?page=2', ''),
    #                                                  ('1', '?page=2', '&per_page=2'),
    #                                                  ('1', '', '?per_page=2'),
    #                                                  ('1', '', '?per_page=20')])
    # def test_author_books(self, client, _id, page, per_page):
    #     url = "api/author/books/" + _id + page + per_page
    #     response = client.get(url)
    #     assert response.status_code == 200
    #
    # @pytest.mark.parametrize("_id, page, per_page", [('', '', ''),
    #                                                  ('', '?page=2', ''),
    #                                                  ('', '?page=2', '&per_page=2'),
    #                                                  ('', '', '?per_page=2'),
    #                                                  ('', '', '?per_page=20')])
    # def test_book(self, client, _id, page, per_page):
    #     url = "api/book" + _id + page + per_page
    #     response = client.get(url)
    #     assert response.status_code == 200



    # @pytest.mark.parametrize("route, _id", [('author', ''),
    #                                         ('author', ''),
    #                                         ('author', ''),
    #                                         ('author', ''),
    #                                         ('author', ''),
    #                                         ('book', ''),
    #                                         ('book', ''),
    #                                         ('book', ''),
    #                                         ('book', ''),
    #                                         ('book', '')])
    # def test_routes_without_pagination(self, client, route, _id):
    #     url = "api/" + route + _id
    #     response = client.get(url)
    #     assert response.status_code == 200 or response.status_code == 404


# author // book // author/books
# id // None
# page // None
# per_page // None
#