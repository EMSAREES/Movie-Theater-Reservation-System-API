from typing import Optional
from app.repositories.base_repository import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository[User]):

    def __init__(self):
        super().__init__(User)

    def find_by_email(self, email: str) -> Optional[User]:
        """
        Busca un usuario por email (case-insensitive).

        Normalizamos el email a minúsculas en el servicio antes de guardar,
        así que aquí hacemos la búsqueda también en minúsculas.
        """
        return User.query.filter_by(email=email.lower()).first()

    def exists_by_email(self, email: str) -> bool:
        """
        Verifica si ya existe un usuario con ese email.

        Más eficiente que find_by_email() porque no carga el objeto completo.
        """
        return User.query.filter_by(email=email.lower()).first() is not None

    def find_all_active(self) -> list:
        """Devuelve todos los usuarios activos ordenados por nombre."""
        return (
            User.query
            .filter_by(is_active=True)
            .order_by(User.first_name, User.last_name)
            .all()
        )