from typing import List

from app.models.room import Room
from app.repositories.room_repository import RoomRepository
from app.exceptions.app_exceptions import (
    RoomNotFoundException,
    RoomNameAlreadyExistsException,
)


class RoomService:

    def __init__(self):
        self.repo = RoomRepository()

    def get_all_rooms(self) -> List[Room]:
        """Devuelve todas las salas activas."""
        return self.repo.find_all_active()

    def get_room_by_id(self, room_id: int) -> Room:
        """
        Obtiene una sala por ID.

        Raises:
            RoomNotFoundException: si no existe o está inactiva.
        """
        room = self.repo.find_by_id(room_id)
        if not room or not room.is_active:
            raise RoomNotFoundException(room_id)
        return room

    def create_room(self, data: dict) -> Room:
        """
        Crea una nueva sala.

        Reglas de negocio:
          1. El nombre de la sala debe ser único.
          2. total_seats se calcula automáticamente: rows × seats_per_row.

        Args:
            data: Dict validado por RoomCreateSchema.

        Returns:
            Room con id asignado.

        Raises:
            RoomNameAlreadyExistsException: si el nombre ya existe.
        """
        if self.repo.exists_by_name(data['name']):
            raise RoomNameAlreadyExistsException(data['name'])

        room = Room(
            name=data['name'].strip(),
            rows=data['rows'],
            seats_per_row=data['seats_per_row'],
            total_seats=data['rows'] * data['seats_per_row'],   # calculado
            room_type=data.get('room_type', 'standard'),
        )

        self.repo.save(room)
        self.repo.commit()

        return room

    def update_room(self, room_id: int, data: dict) -> Room:
        """
        Actualiza los campos de una sala.

        Si cambian rows o seats_per_row, recalcula total_seats.

        Raises:
            RoomNotFoundException: si la sala no existe.
            RoomNameAlreadyExistsException: si el nuevo nombre ya existe.
        """
        room = self.get_room_by_id(room_id)

        if 'name' in data and data['name'].lower() != room.name.lower():
            if self.repo.exists_by_name(data['name'], exclude_id=room_id):
                raise RoomNameAlreadyExistsException(data['name'])

        for field, value in data.items():
            setattr(room, field, value)

        # Recalcular capacidad si cambiaron las dimensiones
        if 'rows' in data or 'seats_per_row' in data:
            room.total_seats = room.rows * room.seats_per_row

        self.repo.save(room)
        self.repo.commit()

        return room

    def delete_room(self, room_id: int) -> None:
        """Desactiva una sala (soft delete)."""
        room           = self.get_room_by_id(room_id)
        room.is_active = False
        self.repo.save(room)
        self.repo.commit()