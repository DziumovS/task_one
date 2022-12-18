import pytest


class TestPOSTRequests:
    @pytest.mark.parametrize("name, surname", [(1, 2),
                                               (1, 2)])
    def test_post(self, client, create_tables, name, surname):
        url = "api/author"
        data = {
            "name": "Name58",
            "surname": "Surname58"
        }
        response = client.post(url, json=data)
        assert response.status_code == 201
