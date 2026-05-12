import json
from tests.conftest import auth_header

class TestRoomsEndpoints:

    def test_get_rooms_empty(self, client):
        response = client.get('/api/v1/rooms')

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['data'] == []

    def test_create_room_success(self, client, user_token, sample_room_data):
        response = client.post(
            '/api/v1/rooms',
            json=sample_room_data,
            headers=auth_header(user_token)
        )

        data = json.loads(response.data)

        assert response.status_code == 201
        assert data['data']['name'] == sample_room_data['name']

    def test_create_room_missing_fields(self, client, user_token):
        response = client.post(
            '/api/v1/rooms',
            json={
                'name': 'Sala'
            },
            headers=auth_header(user_token)
        )

        assert response.status_code == 422

    def test_get_room_by_id(self, client, created_room):
        response = client.get(f'/api/v1/rooms/{created_room["id"]}')

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['data']['id'] == created_room['id']

    def test_get_room_not_found(self, client):
        response = client.get('/api/v1/rooms/9999')

        assert response.status_code == 404

    def test_update_room(self, client, user_token, created_room):
        response = client.put(
            f'/api/v1/rooms/{created_room["id"]}',
            json={
                'name': 'Sala VIP'
            },
            headers=auth_header(user_token)
        )

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['data']['name'] == 'Sala VIP'

    def test_delete_room(self, client, user_token, created_room):
        response = client.delete(
            f'/api/v1/rooms/{created_room["id"]}',
            headers=auth_header(user_token)
        )

        assert response.status_code in [200, 204]