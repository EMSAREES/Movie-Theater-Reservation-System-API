from marshmallow import ValidationError

from app.services.room_service  import RoomService
from app.schemas.room_schema    import (
    room_create_schema,
    room_update_schema,
    room_response_schema,
    rooms_response_schema,
)
from app.utils.response_helper  import (
    success_response, error_response, created_response, no_content_response
)
from app.exceptions.app_exceptions import AppException
from app.controllers.base_controller import get_json_body, flatten_validation_errors


class RoomController:

    def __init__(self):
        self.service = RoomService()

    # ── GET /api/v1/rooms ──────────────────────────────────────────────────────

    def get_all(self):
        """Lista todas las salas activas."""
        rooms = self.service.get_all_rooms()
        return success_response(
            data=rooms_response_schema.dump(rooms),
            message="Salas obtenidas exitosamente"
        )

    # ── GET /api/v1/rooms/<id> ─────────────────────────────────────────────────

    def get_by_id(self, room_id: int):
        """Detalle de una sala por ID."""
        try:
            room = self.service.get_room_by_id(room_id)
            return success_response(
                data=room_response_schema.dump(room),
                message="Sala obtenida exitosamente"
            )
        except AppException as e:
            return error_response(e.message, e.status_code)

    # ── POST /api/v1/rooms ─────────────────────────────────────────────────────

    def create(self):
        """Crea una nueva sala. Requiere autenticación JWT."""
        try:
            data, err = get_json_body()
            if err:
                return err

            validated = room_create_schema.load(data)
            room      = self.service.create_room(validated)

            return created_response(
                data=room_response_schema.dump(room),
                message="Sala creada exitosamente"
            )

        except ValidationError as e:
            return error_response(
                "Datos de entrada inválidos",
                422,
                flatten_validation_errors(e.messages)
            )
        except AppException as e:
            return error_response(e.message, e.status_code)

    # ── PUT /api/v1/rooms/<id> ─────────────────────────────────────────────────

    def update(self, room_id: int):
        """Actualiza una sala existente."""
        try:
            data, err = get_json_body()
            if err:
                return err

            validated = room_update_schema.load(data)
            room      = self.service.update_room(room_id, validated)

            return success_response(
                data=room_response_schema.dump(room),
                message="Sala actualizada exitosamente"
            )

        except ValidationError as e:
            return error_response(
                "Datos de entrada inválidos",
                422,
                flatten_validation_errors(e.messages)
            )
        except AppException as e:
            return error_response(e.message, e.status_code)

    # ── DELETE /api/v1/rooms/<id> ──────────────────────────────────────────────

    def delete(self, room_id: int):
        """Desactiva (soft-delete) una sala."""
        try:
            self.service.delete_room(room_id)
            return no_content_response()
        except AppException as e:
            return error_response(e.message, e.status_code)