from app.models.user import User
from app.models.movie import Movie
from app.models.room import Room
from app.models.screening import Screening
from app.models.ticket import Ticket

__all__ = ['User', 'Movie', 'Room', 'Screening', 'Ticket']

"""
Importa todos los modelos para que Flask-Migrate los detecte.

Flask-Migrate necesita "ver" todos los modelos para generar
las migraciones correctamente. Si un modelo no se importa
aquí, Migrate no sabrá que existe.
"""