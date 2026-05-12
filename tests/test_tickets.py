import json
from tests.conftest import auth_header


class TestTicketsEndpoints:

    def test_get_tickets_empty(self, client, user_token):
        response = client.get(
            '/api/v1/tickets',
            headers=auth_header(user_token)
        )

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['data'] == []

    def test_create_ticket_success(self, client, user_token, created_screening):
        response = client.post(
            '/api/v1/tickets',
            json={
                'screening_id': created_screening['id'],
                'seat_row': 'A',
                'seat_column': 2
            },
            headers=auth_header(user_token)
        )

        data = json.loads(response.data)

        assert response.status_code == 201
        assert data['success'] is True

    def test_create_ticket_duplicate_seat(self, client, user_token, created_screening):
        payload = {
            'screening_id': created_screening['id'],
            'seat_row': 'A',
            'seat_column': 2
        }

        client.post(
            '/api/v1/tickets',
            json=payload,
            headers=auth_header(user_token)
        )

        response = client.post(
            '/api/v1/tickets',
            json=payload,
            headers=auth_header(user_token)
        )

        assert response.status_code in [400, 409]

    def test_get_ticket_by_id(self, client, user_token, created_screening):
        create_response = client.post(
            '/api/v1/tickets',
            json={
                'screening_id': created_screening['id'],
                'seat_row': 'A',
                'seat_column': 3
            },
            headers=auth_header(user_token)
        )

        ticket = json.loads(create_response.data)['data']

        response = client.get(
            f'/api/v1/tickets/{ticket["id"]}',
            headers=auth_header(user_token)
        )

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['data']['id'] == ticket['id']

    def test_cancle_ticket(self, client, user_token, created_screening):
        create_response = client.post(
            '/api/v1/tickets',
            json={
                'screening_id': created_screening['id'],
                'seat_row': 'A',
                'seat_column': 2
            },
            headers=auth_header(user_token)
        )

        ticket = json.loads(create_response.data)['data']

        response = client.post(
            f'/api/v1/tickets/{ticket["id"]}/cancel',
            headers=auth_header(user_token)
        )
        assert response.status_code in [200, 204]
