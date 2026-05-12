from datetime import datetime, timezone
from app.repositories.ticket_repository import TicketRepository, ScreeningRepository
from app.exceptions.app_exceptions import (
    TicketNotFoundException,
    ScreeningNotFoundException,
    SeatAlreadyTakenException,
    ScreeningFullException,
    ScreeningAlreadyStartedException,
    BusinessRuleException,
    ForbiddenException
)


class TicketService:
    
    def __init__(self):
        self.ticket_repo = TicketRepository()
        self.screening_repo = ScreeningRepository()
    
    def purchase_ticket(self, user_id: int, data: dict):
        """
        Compra un ticket para una función.
        
        Flujo completo:
        1. Verificar que la función existe y está disponible
        2. Construir el código del asiento
        3. Verificar que el asiento está libre
        4. Crear el ticket
        5. Actualizar asientos vendidos en la función
        
        ¡IMPORTANTE SOBRE CONCURRENCIA!
        En producción real este proceso debería usar:
        - Transacciones con SELECT FOR UPDATE (bloqueo pesimista)
        - O algún sistema de reserva temporal (Redis)
        Para este tutorial usamos la UniqueConstraint de la BD
        como última línea de defensa.
        """
        from app.models.ticket import Ticket
        
        screening_id = data['screening_id']
        seat_row = data['seat_row'].upper()
        seat_column = data['seat_column']
        
        # 1. Verificar que la función existe
        screening = self.screening_repo.find_by_id_with_relations(screening_id)
        if not screening:
            raise ScreeningNotFoundException(screening_id)
        
        # 2. Regla de negocio: la función debe estar disponible
        if screening.status != 'scheduled':
            raise BusinessRuleException(
                f"La función tiene estado '{screening.status}' y no acepta reservas"
            )
        
        # 3. Regla de negocio: la función no ha comenzado
        now = datetime.now(timezone.utc)
        if screening.start_time <= now:
            raise ScreeningAlreadyStartedException()
        
        # 4. Regla de negocio: hay asientos disponibles
        if screening.is_full:
            raise ScreeningFullException()
        
        # 5. Validar que el asiento existe en la sala
        room = screening.room
        col_letter_index = ord(seat_row) - ord('A')  # A=0, B=1, C=2...
        if col_letter_index >= room.rows or seat_column > room.seats_per_row:
            raise BusinessRuleException(
                f"El asiento {seat_row}{seat_column} no existe en esta sala"
            )
        
        # 6. Construir el código del asiento: "A5", "B10"
        seat_number = f"{seat_row}{seat_column}"
        
        # 7. Verificar que el asiento no está ocupado
        existing = self.ticket_repo.find_by_screening_and_seat(
            screening_id, seat_number
        )
        if existing:
            raise SeatAlreadyTakenException(seat_number)
        
        # 8. Crear el ticket
        ticket = Ticket(
            user_id=user_id,
            screening_id=screening_id,
            seat_number=seat_number,
            seat_row=seat_row,
            seat_column=seat_column,
            price_paid=screening.price,
            status='reserved'
        )
        
        # 9. Actualizar contador de asientos vendidos
        screening.sold_seats += 1
        
        # 10. Guardar ambos cambios en la misma transacción
        self.ticket_repo.save(ticket)
        self.screening_repo.save(screening)
        self.ticket_repo.commit()
        
        return ticket
    
    def cancel_ticket(self, ticket_id: int, user_id: int):
        """
        Cancela un ticket.
        
        Reglas:
        - Solo el dueño del ticket puede cancelarlo
        - No se puede cancelar si la función ya comenzó
        - No se puede cancelar un ticket ya cancelado
        """
        ticket = self.ticket_repo.find_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundException(ticket_id)
        
        # El usuario solo puede cancelar SUS propios tickets
        if ticket.user_id != user_id:
            raise ForbiddenException("No puedes cancelar un ticket que no es tuyo")
        
        # No se puede cancelar algo ya cancelado
        if ticket.status == 'cancelled':
            raise BusinessRuleException("Este ticket ya está cancelado")
        
        # No se puede cancelar si la función ya comenzó
        now = datetime.now(timezone.utc)
        if ticket.screening.start_time <= now:
            raise BusinessRuleException(
                "No puedes cancelar un ticket para una función que ya comenzó"
            )
        
        # Cancelar y liberar el asiento
        ticket.cancel()
        ticket.screening.sold_seats = max(0, ticket.screening.sold_seats - 1)
        
        self.ticket_repo.save(ticket)
        self.ticket_repo.commit()
        
        return ticket
    
    def get_ticket_by_id(self, ticket_id: int, user_id: int):
        """Solo el dueño puede ver los detalles de su ticket."""
        ticket = self.ticket_repo.find_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundException(ticket_id)
        if ticket.user_id != user_id:
            raise ForbiddenException("No tienes acceso a este ticket")
        return ticket
    
    def get_user_tickets(self, user_id: int, page: int, per_page: int):
        return self.ticket_repo.find_by_user_paginated(user_id, page, per_page)
    
    def get_seats_map(self, screening_id: int) -> dict:
        """
        Devuelve mapa de asientos de una función:
        qué asientos están disponibles y cuáles ocupados.
        """
        screening = self.screening_repo.find_by_id_with_relations(screening_id)
        if not screening:
            raise ScreeningNotFoundException(screening_id)
        
        taken_seats = self.ticket_repo.find_seats_taken(screening_id)
        room = screening.room
        
        # Generar mapa completo de todos los asientos
        seats = []
        for row_index in range(room.rows):
            row_letter = chr(ord('A') + row_index)
            for col in range(1, room.seats_per_row + 1):
                seat_number = f"{row_letter}{col}"
                seats.append({
                    "seat_number": seat_number,
                    "row": row_letter,
                    "column": col,
                    "is_taken": seat_number in taken_seats
                })
        
        return {
            "screening_id": screening_id,
            "total_seats": room.total_seats,
            "available_seats": screening.available_seats,
            "sold_seats": screening.sold_seats,
            "seats": seats
        }
    


"""
Servicio de Tickets — La lógica de negocio más importante del sistema.

Las reglas de negocio más críticas están aquí:
- ¿Puede comprarse un ticket para esta función?
- ¿Está disponible el asiento solicitado?
- ¿La función ya comenzó?
- ¿Se puede cancelar este ticket?
"""