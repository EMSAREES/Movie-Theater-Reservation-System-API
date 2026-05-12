from flask import request
from marshmallow import ValidationError
from typing import Tuple, Optional

from app.utils.response_helper import error_response
from app.exceptions.app_exceptions import AppException


def get_json_body() -> Tuple[Optional[dict], Optional[tuple]]:
    """
    Extrae el body JSON del request actual.

    Returns:
        (data, None)       si el body es JSON válido.
        (None, response)   si falta el body o no es JSON.
    """
    data = request.get_json(silent=True)
    if data is None:
        return None, error_response(
            "Se requiere un body JSON con Content-Type: application/json",
            400
        )
    return data, None


def flatten_validation_errors(errors: dict) -> list:
    """
    Convierte el dict de errores de Marshmallow a lista plana de strings.

    Marshmallow devuelve:
      { 'title': ['El campo es requerido'], 'price': ['Debe ser positivo'] }

    Nosotros devolvemos:
      ['title: El campo es requerido', 'price: Debe ser positivo']

    También maneja errores anidados:
      { 'screening': { 'movie_id': ['Inválido'] } }
      → ['screening.movie_id: Inválido']
    """
    flat: list = []

    def _recurse(errs: dict, prefix: str = '') -> None:
        for field, messages in errs.items():
            key = f"{prefix}.{field}" if prefix else field
            if isinstance(messages, list):
                for msg in messages:
                    flat.append(f"{key}: {msg}")
            elif isinstance(messages, dict):
                _recurse(messages, prefix=key)

    _recurse(errors)
    return flat


def handle_request(service_call, schema_load=None, json_required=True):
    """
    Wrapper genérico para el patrón estándar de un controlador:
      1. Extraer JSON (opcional).
      2. Validar con schema (opcional).
      3. Llamar al servicio.
      4. Capturar ValidationError y AppException.

    Diseñado para casos simples; los controladores complejos implementan
    su propio try/except para mayor control.
    """
    try:
        data = None
        if json_required:
            data, err = get_json_body()
            if err:
                return err

        if schema_load is not None and data is not None:
            data = schema_load(data)

        return service_call(data)

    except ValidationError as e:
        return error_response(
            "Datos de entrada inválidos",
            422,
            flatten_validation_errors(e.messages)
        )
    except AppException as e:
        return error_response(e.message, e.status_code)
    
"""
Controlador Base — helpers compartidos por todos los controladores.

Centraliza:
  - Extracción y parseo del JSON del body.
  - Aplanado de errores de validación de Marshmallow.
  - Patrón try/except estándar.

Los controladores concretos importan estas funciones en vez de
duplicar la misma lógica en cada uno.
"""