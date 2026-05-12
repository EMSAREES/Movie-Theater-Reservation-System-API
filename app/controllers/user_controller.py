from flask import request
from marshmallow import ValidationError

from app.services.user_service  import UserService
from app.schemas.user_schema    import (
    user_register_schema,
    user_login_schema,
    user_response_schema,
)
from app.utils.response_helper  import success_response, error_response, created_response
from app.exceptions.app_exceptions import AppException
from app.controllers.base_controller import get_json_body, flatten_validation_errors


class UserController:

    def __init__(self):
        self.service = UserService()

    # ── POST /api/v1/users/register ────────────────────────────────────────────

    def register(self):
        """
        Registra un nuevo usuario.

        Body JSON requerido:
          { "first_name": "...", "last_name": "...", "email": "...", "password": "..." }

        Responses:
          201 Created  → usuario creado
          422          → datos inválidos
          409          → email ya registrado
        """
        try:
            data, err = get_json_body()
            if err:
                return err

            validated = user_register_schema.load(data)
            user      = self.service.register(validated)

            return created_response(
                data=user_response_schema.dump(user),
                message="Usuario registrado exitosamente"
            )

        except ValidationError as e:
            return error_response(
                "Datos de registro inválidos",
                422,
                flatten_validation_errors(e.messages)
            )
        except AppException as e:
            return error_response(e.message, e.status_code)

    # ── POST /api/v1/users/login ───────────────────────────────────────────────

    def login(self):
        """
        Autentica al usuario y devuelve un JWT.

        Body JSON requerido:
          { "email": "...", "password": "..." }

        Responses:
          200 OK       → login exitoso, incluye access_token
          401          → credenciales incorrectas
          422          → datos inválidos
        """
        try:
            data, err = get_json_body()
            if err:
                return err

            validated = user_login_schema.load(data)
            result    = self.service.login(validated)

            return success_response(
                data={
                    "access_token": result['access_token'],
                    "token_type":   result['token_type'],
                    "user":         user_response_schema.dump(result['user']),
                },
                message="Sesión iniciada exitosamente"
            )

        except ValidationError as e:
            return error_response(
                "Datos de login inválidos",
                422,
                flatten_validation_errors(e.messages)
            )
        except AppException as e:
            return error_response(e.message, e.status_code)
        

"""
Controlador de Usuarios.

Responsabilidades:
  1. Recibir el request HTTP.
  2. Extraer y validar los datos con el schema correspondiente.
  3. Llamar al servicio.
  4. Capturar excepciones y convertirlas en respuestas HTTP.
  5. Serializar el resultado.

El controlador NO contiene lógica de negocio.
Si empieza a crecer con condiciones de negocio, es señal de que
esa lógica debería estar en el servicio.
"""
