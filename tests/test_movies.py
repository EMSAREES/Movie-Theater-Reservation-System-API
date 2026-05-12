import json
from tests.conftest import auth_header


class TestMoviesEndpoints:

    def test_get_movies_empty(self, client):
        response = client.get('/api/v1/movies')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['data'] == []

    def test_create_movie_success(self, client, user_token, sample_movie_data):
        response = client.post(
            '/api/v1/movies',
            json=sample_movie_data,
            headers=auth_header(user_token)
        )

        data = json.loads(response.data)

        assert response.status_code == 201
        assert data['success'] is True
        assert data['data']['title'] == sample_movie_data['title']

    def test_create_movie_unauthorized(self, client, sample_movie_data):
        response = client.post('/api/v1/movies', json=sample_movie_data)

        assert response.status_code in [401, 422]

    def test_create_movie_missing_title(self, client, user_token):
        response = client.post(
            '/api/v1/movies',
            json={
                'duration_minutes': 120,
                'genre': 'Action'
            },
            headers=auth_header(user_token)
        )

        assert response.status_code == 422

    def test_get_movie_by_id(self, client, created_movie):
        response = client.get(f'/api/v1/movies/{created_movie["id"]}')

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['data']['id'] == created_movie['id']

    def test_get_movie_not_found(self, client):
        response = client.get('/api/v1/movies/9999')

        assert response.status_code == 404

    def test_update_movie_success(self, client, user_token, created_movie):
        response = client.put(
            f'/api/v1/movies/{created_movie["id"]}',
            json={
                'title': 'Nuevo Titulo'
            },
            headers=auth_header(user_token)
        )

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['data']['title'] == 'Nuevo Titulo'

    def test_delete_movie_success(self, client, user_token, created_movie):
        response = client.delete(
            f'/api/v1/movies/{created_movie["id"]}',
            headers=auth_header(user_token)
        )

        assert response.status_code in [200, 204]