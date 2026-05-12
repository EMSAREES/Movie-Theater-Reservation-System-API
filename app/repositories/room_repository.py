from typing import Optional, List
from app.repositories.base_repository import BaseRepository
from app.models.room import Room


class RoomRepository(BaseRepository[Room]):

    def __init__(self):
        super().__init__(Room)

    def find_all_active(self) -> List[Room]:
        """Devuelve todas las salas activas ordenadas alfabéticamente."""
        return (
            Room.query
            .filter_by(is_active=True)
            .order_by(Room.name)
            .all()
        )

    def find_by_name(self, name: str) -> Optional[Room]:
        """Busca una sala por nombre exacto (case-insensitive)."""
        return Room.query.filter(Room.name.ilike(name.strip())).first()

    def exists_by_name(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe una sala con ese nombre.
        exclude_id: al actualizar, excluye la propia sala de la verificación.
        """
        query = Room.query.filter(Room.name.ilike(name.strip()))
        if exclude_id is not None:
            query = query.filter(Room.id != exclude_id)
        return query.first() is not None