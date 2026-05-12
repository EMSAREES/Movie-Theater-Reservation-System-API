import json
import pytest
from tests.conftest import register_user, login_user, auth_header


class TestUserRegister:
    """POST /api/v1/users/register"""

    def test_register_success(self, client):
        """Registro correcto devuelve 201 con datos del usuario."""
        resp = register_user(client, email="nuevo@test.com")
        data = json.loads(resp.data)

        assert resp.status_code == 201
        assert data['success'] is True
        assert data['data']['email'] == "nuevo@test.com"
        assert 'password_hash' not in data['data']   # NUNCA exponer el hash
        assert 'password' not in data['data']

    def test_register_returns_user_fields(self, client):
        """La respuesta incluye todos los campos del usuario."""
        resp = register_user(client, first_name="Ana", last_name="López")
        data = json.loads(resp.data)['data']

        assert 'id' in data
        assert 'first_name' in data
        assert 'last_name' in data
        assert 'email' in data
        assert 'role' in data
        assert 'is_active' in data
        assert data['role'] == 'customer'
        assert data['is_active'] is True

    def test_register_duplicate_email_returns_409(self, client):
        """Registrar el mismo email dos veces devuelve 409 Conflict."""
        register_user(client, email="dup@test.com")
        resp = register_user(client, email="dup@test.com")
        data = json.loads(resp.data)

        assert resp.status_code == 409
        assert data['success'] is False

    def test_register_email_case_insensitive(self, client):
        """Emails en diferente case se tratan como el mismo."""
        register_user(client, email="case@test.com")
        resp = register_user(client, email="CASE@TEST.COM")

        assert resp.status_code == 409

    def test_register_missing_required_fields(self, client):
        """Faltar campos requeridos devuelve 422."""
        resp = client.post('/api/v1/users/register', json={
            "email": "solo@email.com"
            # Faltan: first_name, last_name, password
        })
        data = json.loads(resp.data)

        assert resp.status_code == 422
        assert data['success'] is False
        assert len(data['errors']) > 0

    def test_register_invalid_email(self, client):
        """Email con formato inválido devuelve 422."""
        resp = client.post('/api/v1/users/register', json={
            "first_name": "Test",
            "last_name": "User",
            "email": "esto-no-es-un-email",
            "password": "password1",
        })
        data = json.loads(resp.data)

        assert resp.status_code == 422
        assert data['success'] is False

    def test_register_short_password(self, client):
        """Contraseña menor a 8 caracteres devuelve 422."""
        resp = client.post('/api/v1/users/register', json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@test.com",
            "password": "abc1",  # muy corta
        })
        assert resp.status_code == 422

    def test_register_password_no_digit(self, client):
        """Contraseña sin número devuelve 422."""
        resp = client.post('/api/v1/users/register', json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@test.com",
            "password": "sindigitos",
        })
        assert resp.status_code == 422

    def test_register_password_no_letter(self, client):
        """Contraseña sin letra devuelve 422."""
        resp = client.post('/api/v1/users/register', json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@test.com",
            "password": "12345678",
        })
        assert resp.status_code == 422

    def test_register_no_json_body(self, client):
        """Request sin body JSON devuelve 400."""
        resp = client.post('/api/v1/users/register')
        assert resp.status_code == 400

    def test_register_passwords_mismatch(self, client):
        """Si se envía password_confirm y no coincide, devuelve 422."""
        resp = client.post('/api/v1/users/register', json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@test.com",
            "password": "password1",
            "password_confirm": "diferente2",
        })
        assert resp.status_code == 422


class TestUserLogin:
    """POST /api/v1/users/login"""

    def test_login_success(self, client):
        """Login correcto devuelve 200 con JWT."""
        register_user(client)
        resp = client.post('/api/v1/users/login', json={
            "email": "user@test.com",
            "password": "password1",
        })
        data = json.loads(resp.data)

        assert resp.status_code == 200
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert data['data']['token_type'] == 'Bearer'
        assert 'user' in data['data']

    def test_login_wrong_password(self, client):
        """Contraseña incorrecta devuelve 401."""
        register_user(client)
        resp = client.post('/api/v1/users/login', json={
            "email": "user@test.com",
            "password": "wrongpass9",
        })
        data = json.loads(resp.data)

        assert resp.status_code == 401
        assert data['success'] is False

    def test_login_nonexistent_email(self, client):
        """Email que no existe devuelve 401 (mismo mensaje que wrong password)."""
        resp = client.post('/api/v1/users/login', json={
            "email": "noexiste@test.com",
            "password": "password1",
        })
        assert resp.status_code == 401

    def test_login_email_case_insensitive(self, client):
        """Login con email en mayúsculas funciona igual."""
        register_user(client, email="lower@test.com")
        resp = client.post('/api/v1/users/login', json={
            "email": "LOWER@TEST.COM",
            "password": "password1",
        })
        assert resp.status_code == 200

    def test_login_missing_fields(self, client):
        """Faltar email o password devuelve 422."""
        resp = client.post('/api/v1/users/login', json={"email": "test@test.com"})
        assert resp.status_code == 422

    def test_login_no_json(self, client):
        """Request sin body devuelve 400."""
        resp = client.post('/api/v1/users/login')
        assert resp.status_code == 400

    def test_login_token_is_usable(self, client):
        """El token recibido en login funciona para endpoints protegidos."""
        register_user(client)
        token = login_user(client)

        resp = client.get(
            '/api/v1/tickets',
            headers=auth_header(token)
        )
        assert resp.status_code == 200
