class TestHealth:

    def test_health_check(self, client):
        response = client.get('/')

        assert response.status_code == 200