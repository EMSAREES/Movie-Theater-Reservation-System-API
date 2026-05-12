import json
from datetime import datetime, timezone, timedelta
from tests.conftest import auth_header


class TestScreeningsEndpoints:

    def test_get_screenings_empty(self, client):
        response = client.get('/api/v1/screenings')

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['data'] == []

    def test_create_screening_success(self, client, user_token, created_movie, created_room):
        future_time = datetime.now(timezone.utc) + timedelta(days=1)

        response = client.post(
            '/api/v1/screenings',
            json={
                'movie_id': created_movie['id'],
                'room_id': created_room['id'],
                'start_time': future_time.isoformat(),
                'price': '150.00',
                'language': 'Español',
                'format': '2D'
            },
            headers=auth_header(user_token)
        )

        data = json.loads(response.data)

        assert response.status_code == 201
        assert data['data']['movie_id'] == created_movie['id']

    def test_create_screening_invalid_movie(self, client, user_token, created_room):
        future_time = datetime.now(timezone.utc) + timedelta(days=1)

        response = client.post(
            '/api/v1/screenings',
            json={
                'movie_id': 999,
                'room_id': created_room['id'],
                'start_time': future_time.isoformat(),
                'price': '150.00'
            },
            headers=auth_header(user_token)
        )

        assert response.status_code in [400, 404]

    def test_get_screening_by_id(self, client, created_screening):
        response = client.get(f'/api/v1/screenings/{created_screening["id"]}')

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['data']['id'] == created_screening['id']

