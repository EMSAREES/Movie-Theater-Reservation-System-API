from typing import Optional, List
from datetime import date as date_type
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from app.repositories.base_repository import BaseRepository
from app.models.screening import Screening
from app.utils.pagination import paginate_query


class ScreeningRepository(BaseRepository[Screening]):

    def __init__(self):
        super().__init__(Screening)

    def find_by_id_with_relations(self, screening_id: int) -> Optional[Screening]:
        """
        Carga la función junto con su película y sala en una sola query.

        Equivalente SQL aproximado:
          SELECT screenings.*, movies.*, rooms.*
          FROM screenings
          JOIN movies ON screenings.movie_id = movies.id
          JOIN rooms  ON screenings.room_id  = rooms.id
          WHERE screenings.id = :id
        """
        return (
            Screening.query
            .options(
                joinedload(Screening.movie),
                joinedload(Screening.room),
            )
            .filter_by(id=screening_id)
            .first()
        )

    def find_all_paginated(
        self,
        page:     int,
        per_page: int,
        movie_id: Optional[int]       = None,
        date:     Optional[date_type] = None,
    ) -> dict:
        """
        Lista funciones programadas con paginación y filtros opcionales.

        Filtros disponibles:
          movie_id → solo funciones de esa película
          date     → solo funciones de ese día (ignora la hora)

        Siempre ordena por start_time ascendente (próximas primero).
        """
        query = (
            Screening.query
            .options(
                joinedload(Screening.movie),
                joinedload(Screening.room),
            )
            .filter(Screening.status == 'scheduled')
        )

        if movie_id is not None:
            query = query.filter(Screening.movie_id == movie_id)

        if date is not None:
            # func.date() extrae solo la parte de fecha del TIMESTAMP
            query = query.filter(func.date(Screening.start_time) == date)

        query = query.order_by(Screening.start_time.asc())

        return paginate_query(query, page, per_page)

    def find_by_room_and_time(
        self,
        room_id:    int,
        start_time,
    ) -> Optional[Screening]:
        """
        Verifica si ya existe una función en esa sala a esa hora.
        Usado para detectar conflictos de horario antes de crear una nueva función.
        """
        return Screening.query.filter_by(
            room_id=room_id,
            start_time=start_time,
        ).first()

"""
Repositorio de Funciones (Screening).

Carga las relaciones movie y room con joinedload para evitar el
problema N+1: sin joinedload, acceder a screening.movie dentro de
un bucle dispararía una query extra por cada iteración.
Con joinedload, SQLAlchemy hace un JOIN y trae todo en una sola query.
"""