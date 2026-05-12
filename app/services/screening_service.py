from datetime import datetime, timezone, timedelta
from typing import Optional
from datetime import date as date_type

from app import db
from app.models.screening import Screening
from app.repositories.screening_repository import ScreeningRepository
from app.repositories.movie_repository     import MovieRepository
from app.repositories.room_repository      import RoomRepository
from app.exceptions.app_exceptions import (
    ScreeningNotFoundException,
    MovieNotFoundException,
    RoomNotFoundException,
    ConflictException,
    BusinessRuleException,
)


class ScreeningService:

    def __init__(self):
        self.repo       = ScreeningRepository()
        self.movie_repo = MovieRepository()
        self.room_repo  = RoomRepository()

    # ── Consultas ──────────────────────────────────────────────────────────────

    def get_all_screenings(
        self,
        page:     int,
        per_page: int,
        movie_id: Optional[int]       = None,
        date:     Optional[date_type] = None,
    ) -> dict:
        """Lista funciones programadas con paginación y filtros."""
        return self.repo.find_all_paginated(
            page=page,
            per_page=per_page,
            movie_id=movie_id,
            date=date,
        )

    def get_screening_by_id(self, screening_id: int) -> Screening:
        """
        Obtiene una función por ID con sus relaciones cargadas.

        Raises:
            ScreeningNotFoundException: si no existe.
        """
        screening = self.repo.find_by_id_with_relations(screening_id)
        if not screening:
            raise ScreeningNotFoundException(screening_id)
        return screening

    # ── Creación ───────────────────────────────────────────────────────────────

    def create_screening(self, data: dict) -> Screening:
        """
        Crea una nueva función.

        Reglas de negocio:
          1. La película debe existir y estar activa.
          2. La sala debe existir y estar activa.
          3. La sala no puede tener otra función al mismo instante.
          4. end_time = start_time + duración de la película.

        Args:
            data: Dict validado por ScreeningCreateSchema.

        Returns:
            Screening con id asignado y relaciones cargadas.

        Raises:
            MovieNotFoundException    : película no existe o inactiva.
            RoomNotFoundException     : sala no existe o inactiva.
            ConflictException         : sala ya ocupada a esa hora.
        """
        # 1. Verificar película
        movie = self.movie_repo.find_by_id_active(data['movie_id'])
        if not movie:
            raise MovieNotFoundException(data['movie_id'])

        # 2. Verificar sala
        room = self.room_repo.find_by_id(data['room_id'])
        if not room or not room.is_active:
            raise RoomNotFoundException(data['room_id'])

        # 3. Verificar conflicto de horario en la sala
        start_time = data['start_time']
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        existing = self.repo.find_by_room_and_time(data['room_id'], start_time)
        if existing:
            raise ConflictException(
                f"La sala '{room.name}' ya tiene una función programada "
                f"para {start_time.strftime('%Y-%m-%d %H:%M')}"
            )

        # 4. Calcular end_time
        end_time = start_time + timedelta(minutes=movie.duration_minutes)

        screening = Screening(
            movie_id=data['movie_id'],
            room_id=data['room_id'],
            start_time=start_time,
            end_time=end_time,
            price=data['price'],
            language=data.get('language', 'español'),
            format=data.get('format', '2D'),
        )

        self.repo.save(screening)
        self.repo.commit()

        # Recargar con relaciones para serializar correctamente
        return self.repo.find_by_id_with_relations(screening.id)

    # ── Actualización ──────────────────────────────────────────────────────────

    def update_screening(self, screening_id: int, data: dict) -> Screening:
        """
        Actualiza precio, idioma, formato o estado de una función.

        No permite cambiar movie_id ni room_id en un update
        (requeriría recalcular end_time y verificar conflictos nuevamente;
        en ese caso es mejor cancelar y crear una nueva función).

        Raises:
            ScreeningNotFoundException: si la función no existe.
            BusinessRuleException     : si se intenta modificar una función cancelada.
        """
        screening = self.get_screening_by_id(screening_id)

        if screening.status == 'cancelled':
            raise BusinessRuleException("No se puede modificar una función cancelada")

        for field, value in data.items():
            setattr(screening, field, value)

        self.repo.save(screening)
        self.repo.commit()

        return self.repo.find_by_id_with_relations(screening_id)

    def cancel_screening(self, screening_id: int) -> Screening:
        """
        Cancela una función programada.

        En un sistema real deberías también cancelar los tickets activos
        y emitir reembolsos.  Aquí marcamos el estado como 'cancelled'.

        Raises:
            ScreeningNotFoundException : si no existe.
            BusinessRuleException     : si ya está cancelada o ya inició.
        """
        screening = self.get_screening_by_id(screening_id)

        if screening.status == 'cancelled':
            raise BusinessRuleException("La función ya está cancelada")

        now = datetime.now(timezone.utc)
        if screening.start_time <= now:
            raise BusinessRuleException(
                "No se puede cancelar una función que ya inició o finalizó"
            )

        screening.status = 'cancelled'
        self.repo.save(screening)
        self.repo.commit()

        return screening