from typing import Optional, List
from app.repositories.base_repository import BaseRepository
from app.models.ticket import Ticket
from app.utils.pagination import paginate_query


class TicketRepository(BaseRepository[Ticket]):
    
    def __init__(self):
        super().__init__(Ticket)
    
    def find_by_code(self, ticket_code: str) -> Optional[Ticket]:
        """Busca un ticket por su código único legible."""
        return Ticket.query.filter_by(ticket_code=ticket_code.upper()).first()
    
    def find_by_screening_and_seat(
        self,
        screening_id: int,
        seat_number: str
    ) -> Optional[Ticket]:
        """
        Verifica si un asiento específico ya está tomado.
        
        Esto es crítico: debe ejecutarse dentro de una transacción
        para evitar race conditions (dos usuarios comprando el mismo asiento).
        """
        return Ticket.query.filter_by(
            screening_id=screening_id,
            seat_number=seat_number,
            # Solo consideramos tickets activos, no los cancelados
        ).filter(Ticket.status != 'cancelled').first()
    
    def find_seats_taken(self, screening_id: int) -> List[str]:
        """
        Devuelve lista de asientos ocupados para una función.
        
        Útil para mostrar el mapa de asientos al cliente.
        """
        tickets = Ticket.query.filter(
            Ticket.screening_id == screening_id,
            Ticket.status != 'cancelled'
        ).with_entities(Ticket.seat_number).all()
        
        return [t.seat_number for t in tickets]
    
    def find_by_user_paginated(
        self,
        user_id: int,
        page: int,
        per_page: int
    ) -> dict:
        """Tickets de un usuario específico con paginación."""
        query = Ticket.query.filter_by(user_id=user_id).order_by(
            Ticket.purchased_at.desc()
        )
        return paginate_query(query, page, per_page)


class ScreeningRepository(BaseRepository):
    
    def __init__(self):
        from app.models.screening import Screening
        super().__init__(Screening)
    
    def find_by_id_with_relations(self, screening_id: int):
        """
        Carga la función con sus relaciones (película y sala).
        
        joinedload evita el problema N+1:
        Si accedes a screening.movie en un loop sin esto,
        SQLAlchemy hace UNA query por cada iteración.
        Con joinedload hace UN JOIN y trae todo de una vez.
        """
        from app.models.screening import Screening
        from sqlalchemy.orm import joinedload
        
        return Screening.query.options(
            joinedload(Screening.movie),
            joinedload(Screening.room)
        ).filter_by(id=screening_id).first()
    
    def find_all_paginated(self, page: int, per_page: int, movie_id=None, date=None) -> dict:
        from app.models.screening import Screening
        from sqlalchemy.orm import joinedload
        from datetime import datetime, timezone
        
        query = Screening.query.options(
            joinedload(Screening.movie),
            joinedload(Screening.room)
        ).filter(Screening.status == 'scheduled')
        
        if movie_id:
            query = query.filter(Screening.movie_id == movie_id)
        
        if date:
            # Filtrar por fecha (ignorando la hora)
            from sqlalchemy import func
            query = query.filter(
                func.date(Screening.start_time) == date
            )
        
        query = query.order_by(Screening.start_time.asc())
        return paginate_query(query, page, per_page)


class UserRepository(BaseRepository):
    
    def __init__(self):
        from app.models.user import User
        super().__init__(User)
    
    def find_by_email(self, email: str):
        from app.models.user import User
        return User.query.filter_by(email=email.lower()).first()
    
    def exists_by_email(self, email: str) -> bool:
        from app.models.user import User
        return User.query.filter_by(email=email.lower()).first() is not None


class RoomRepository(BaseRepository):
    
    def __init__(self):
        from app.models.room import Room
        super().__init__(Room)
    
    def find_all_active(self):
        from app.models.room import Room
        return Room.query.filter_by(is_active=True).order_by(Room.name).all()