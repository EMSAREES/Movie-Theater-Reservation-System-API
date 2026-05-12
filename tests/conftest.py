
"""
conftest.py — Fixtures globales de pytest.

pytest carga este archivo automáticamente antes de correr los tests.
Los fixtures definidos aquí están disponibles en TODOS los archivos de test
sin necesidad de importarlos.
"""

import json
import pytest
from app import create_app, db as _db


# ── App & DB ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope='session')
def app():
    """
    Instancia de la app con configuración 'testing'.
    scope='session' → se crea UNA sola vez para toda la sesión.
    """
    application = create_app('testing')
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """
    Cliente HTTP para hacer requests en tests.
    scope='function' → se recrea para cada test (aislamiento total).
    """
    return app.test_client()


@pytest.fixture(scope='function', autouse=True)
def clean_db(app):
    """
    Limpia todas las tablas antes de cada test.
    autouse=True → se aplica automáticamente sin necesidad de pedirlo.
    El orden de eliminación respeta las foreign keys (inverso al de creación).
    """
    with app.app_context():
        yield
        _db.session.remove()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


# ── Helpers de autenticación ───────────────────────────────────────────────────

def register_user(client, email="user@test.com", password="password1",
                  first_name="Test", last_name="User"):
    """Helper: registra un usuario y devuelve la respuesta."""
    return client.post('/api/v1/users/register', json={
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
    })


def login_user(client, email="user@test.com", password="password1"):
    """Helper: hace login y devuelve el JWT token."""
    resp = client.post('/api/v1/users/login', json={
        "email": email,
        "password": password,
    })
    data = json.loads(resp.data)
    return data['data']['access_token']


def auth_header(token: str) -> dict:
    """Helper: devuelve el header Authorization con el JWT."""
    return {"Authorization": f"Bearer {token}"}


# ── Fixtures de datos ──────────────────────────────────────────────────────────

@pytest.fixture
def user_token(client):
    """Registra un usuario y devuelve su JWT listo para usar."""
    register_user(client)
    return login_user(client)


@pytest.fixture
def sample_movie_data():
    """Datos válidos para crear una película."""
    return {
        "title": "El Laberinto del Fauno",
        "duration_minutes": 118,
        "genre": "Fantasía,Drama",
        "rating": "R",
        "director": "Guillermo del Toro",
        "language": "Español",
    }


@pytest.fixture
def created_movie(client, user_token, sample_movie_data):
    """Crea una película en la BD y la devuelve como dict."""
    resp = client.post(
        '/api/v1/movies',
        json=sample_movie_data,
        headers=auth_header(user_token)
    )
    return json.loads(resp.data)['data']


@pytest.fixture
def sample_room_data():
    """Datos válidos para crear una sala (4 filas × 5 asientos = 20 total)."""
    return {
        "name": "Sala 1",
        "rows": 4,
        "seats_per_row": 5,
        "room_type": "standard",
    }


@pytest.fixture
def created_room(client, user_token, sample_room_data):
    """Crea una sala en la BD y la devuelve como dict."""
    resp = client.post(
        '/api/v1/rooms',
        json=sample_room_data,
        headers=auth_header(user_token)
    )
    return json.loads(resp.data)['data']


@pytest.fixture
def created_screening(client, user_token, created_movie, created_room):
    """Crea una función en la BD y la devuelve como dict."""
    from datetime import datetime, timezone, timedelta
    future_time = datetime.now(timezone.utc) + timedelta(days=1)

    resp = client.post(
        '/api/v1/screenings',
        json={
            "movie_id": created_movie['id'],
            "room_id": created_room['id'],
            "start_time": future_time.isoformat(),
            "price": "120.00",
            "language": "español",
            "format": "2D",
        },
        headers=auth_header(user_token)
    )
    return json.loads(resp.data)['data']
