from flask import request
from marshmallow import ValidationError

from app.services.screening_service import ScreeningService
from app.schemas.ticket_schema import (
    screening_create_schema,
    screening_response_schema,
    screenings_response_schema,
)
from app.utils.response_helper import (
    success_response, error_response, created_response, no_content_response
)
from app.utils.pagination import get_pagination_params
from app.exceptions.app_exceptions import AppException
from app.controllers.base_controller import get_json_body, flatten_validation_errors


class ScreeningController:
    """
    Controlador de Funciones (Screenings).
    Maneja listado, detalle, creación, actualización y cancelación de funciones.
    """

    def __init__(self):
        self.service = ScreeningService()

    # ── GET /api/v1/screenings ────────────────────────────────────────────────

    def get_all(self):
        """
        Lista funciones programadas con paginación.
        Filtros opcionales: ?movie_id=X  ?date=YYYY-MM-DD
        """
        try:
            page, per_page = get_pagination_params()
            movie_id       = request.args.get('movie_id', type=int)
            date_str       = request.args.get('date')

            date = None
            if date_str:
                from datetime import datetime
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return error_response(
                        "Formato de fecha inválido. Use YYYY-MM-DD", 400
                    )

            result = self.service.get_all_screenings(page, per_page, movie_id, date)
            return success_response(
                data=screenings_response_schema.dump(result['items']),
                message="Funciones obtenidas exitosamente",
                meta=result['meta']
            )
        except AppException as e:
            return error_response(e.message, e.status_code)

    # ── GET /api/v1/screenings/<id> ───────────────────────────────────────────

    def get_by_id(self, screening_id: int):
        """Detalle de una función con sus relaciones."""
        try:
            screening = self.service.get_screening_by_id(screening_id)
            return success_response(
                data=screening_response_schema.dump(screening),
                message="Función obtenida exitosamente"
            )
        except AppException as e:
            return error_response(e.message, e.status_code)

    # ── POST /api/v1/screenings ───────────────────────────────────────────────

    def create(self):
        """Crea una nueva función. Requiere JWT."""
        try:
            data, err = get_json_body()
            if err:
                return err

            validated  = screening_create_schema.load(data)
            screening  = self.service.create_screening(validated)

            return created_response(
                data=screening_response_schema.dump(screening),
                message="Función creada exitosamente"
            )

        except ValidationError as e:
            return error_response(
                "Datos de entrada inválidos", 422,
                flatten_validation_errors(e.messages)
            )
        except AppException as e:
            return error_response(e.message, e.status_code)

    # ── PUT /api/v1/screenings/<id> ───────────────────────────────────────────

    def update(self, screening_id: int):
        """Actualiza precio, idioma, formato o estado de una función."""
        try:
            from app.schemas.ticket_schema import ScreeningUpdateSchema
            data, err = get_json_body()
            if err:
                return err

            validated = ScreeningUpdateSchema().load(data)
            screening = self.service.update_screening(screening_id, validated)

            return success_response(
                data=screening_response_schema.dump(screening),
                message="Función actualizada exitosamente"
            )

        except ValidationError as e:
            return error_response(
                "Datos de entrada inválidos", 422,
                flatten_validation_errors(e.messages)
            )
        except AppException as e:
            return error_response(e.message, e.status_code)

    # ── DELETE /api/v1/screenings/<id> ────────────────────────────────────────

    def cancel(self, screening_id: int):
        """Cancela una función programada. Requiere JWT."""
        try:
            screening = self.service.cancel_screening(screening_id)
            return success_response(
                data=screening_response_schema.dump(screening),
                message="Función cancelada exitosamente"
            )
        except AppException as e:
            return error_response(e.message, e.status_code)

 