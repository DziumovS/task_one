import pytest


@pytest.mark.parametrize("_id", [11, 'cat', 777])
def test_id_exists_11(client, drop_tables, _id):
    url = "api/author/" + str(_id)
    response = client.get(url)
    if _id == 11:
        assert response.status_code == 200
        assert response.json
        assert len(response.json) != 0
        assert len(response.json['author_info']) != 0
        assert len(response.json['author_info']['name']) != 0
        assert len(response.json['author_info']['surname']) != 0
        assert len(response.json['author_info']['created_at']) != 0
        assert response.json['author_info']['id'] == _id
        assert len(response.json['author_books']) == 2
    else:
        assert response.status_code == 404



# def test_id_exists_7(client, drop_tables):
#     url = "api/author/7"
#     response = client.get(url)
#     assert response.status_code == 200
#
#
# def test_post(client):
#     url = "api/author"
#     data = {
#         "name": "Name58",
#         "surname": "Surname58"
#     }
#     response = client.post(url, json=data)
#     assert response.status_code == 201

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
