from flask import request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from app.services.ticket_service import TicketService
from app.schemas.ticket_schema import (
    ticket_create_schema,
    ticket_response_schema,
    tickets_response_schema,
)
from app.utils.response_helper import (
    success_response, error_response, created_response
)
from app.utils.pagination import get_pagination_params
from app.exceptions.app_exceptions import AppException
from app.controllers.base_controller import get_json_body, flatten_validation_errors


class TicketController:
    """
    Controlador de Tickets.
    Maneja compra, cancelación y consulta de tickets.
    """

    def __init__(self):
        self.service = TicketService()

    @staticmethod
    def _get_current_user_id() -> int:
        """Extrae el user_id del JWT token activo."""
        return int(get_jwt_identity())

    # ── POST /api/v1/tickets ──────────────────────────────────────────────────

    def purchase(self):
        """Compra un ticket para una función. Requiere JWT."""
        try:
            user_id = self._get_current_user_id()

            data, err = get_json_body()
            if err:
                return err

            validated = ticket_create_schema.load(data)
            ticket    = self.service.purchase_ticket(user_id, validated)

            return created_response(
                data=ticket_response_schema.dump(ticket),
                message=f"Ticket comprado exitosamente. Código: {ticket.ticket_code}"
            )

        except ValidationError as e:
            return error_response("Datos inválidos", 422, flatten_validation_errors(e.messages))
        except AppException as e:
            return error_response(e.message, e.status_code)

    # ── DELETE /api/v1/tickets/<id> ───────────────────────────────────────────

    def cancel(self, ticket_id: int):
        """Cancela un ticket. Solo el dueño puede cancelarlo."""
        try:
            user_id = self._get_current_user_id()
            ticket  = self.service.cancel_ticket(ticket_id, user_id)

            return success_response(
                data=ticket_response_schema.dump(ticket),
                message="Ticket cancelado exitosamente"
            )
        except AppException as e:
            return error_response(e.message, e.status_code)

    # ── GET /api/v1/tickets/<id> ──────────────────────────────────────────────

    def get_by_id(self, ticket_id: int):
        """Detalle de un ticket. Solo el dueño puede verlo."""
        try:
            user_id = self._get_current_user_id()
            ticket  = self.service.get_ticket_by_id(ticket_id, user_id)
            return success_response(
                data=ticket_response_schema.dump(ticket),
                message="Ticket obtenido exitosamente"
            )
        except AppException as e:
            return error_response(e.message, e.status_code)

    # ── GET /api/v1/tickets ───────────────────────────────────────────────────

    def get_my_tickets(self):
        """Lista los tickets del usuario autenticado con paginación."""
        try:
            user_id        = self._get_current_user_id()
            page, per_page = get_pagination_params()
            result         = self.service.get_user_tickets(user_id, page, per_page)

            return success_response(
                data=tickets_response_schema.dump(result['items']),
                message="Tickets obtenidos exitosamente",
                meta=result['meta']
            )
        except AppException as e:
            return error_response(e.message, e.status_code)

    # ── GET /api/v1/screenings/<id>/seats ─────────────────────────────────────

    def get_seats_map(self, screening_id: int):
        """Mapa de asientos disponibles/ocupados para una función."""
        try:
            seats_data = self.service.get_seats_map(screening_id)
            return success_response(data=seats_data, message="Mapa de asientos obtenido")
        except AppException as e:
            return error_response(e.message, e.status_code)
