from flask import jsonify
from typing import Any, Optional


def success_response(
    data: Any = None,
    message: str = "Operación exitosa",
    status_code: int = 200,
    meta: Optional[dict] = None
):
    """
    Crea una respuesta JSON para operaciones exitosas.
    
    Args:
        data: Los datos a devolver (dict, list, etc.)
        message: Mensaje descriptivo de la operación
        status_code: Código HTTP (200, 201, etc.)
        meta: Información adicional (paginación, totales, etc.)
    
    Returns:
        Tuple[Response, int]: Respuesta Flask con código de estado
    
    Ejemplo de uso:
        return success_response(
            data=movie_schema.dump(movie),
            message="Película creada",
            status_code=201
        )
    """
    response_body = {
        "success": True,
        "message": message,
        "data": data
    }
    
    # Solo incluimos "meta" si se proporciona (para paginación, etc.)
    if meta is not None:
        response_body["meta"] = meta
    
    return jsonify(response_body), status_code


def error_response(
    message: str = "Error en la operación",
    status_code: int = 400,
    errors: Optional[list] = None
):
    """
    Crea una respuesta JSON para errores.
    
    Args:
        message: Descripción general del error
        status_code: Código HTTP de error (400, 404, 409, 500, etc.)
        errors: Lista de errores específicos (útil para validaciones)
    
    Returns:
        Tuple[Response, int]: Respuesta Flask con código de estado
    
    Ejemplo:
        return error_response(
            message="Datos inválidos",
            status_code=422,
            errors=["El email ya está registrado", "El nombre es requerido"]
        )
    """
    response_body = {
        "success": False,
        "message": message,
        "errors": errors or []
    }
    
    return jsonify(response_body), status_code


def created_response(data: Any, message: str = "Recurso creado exitosamente"):
    """Atajo para respuestas 201 Created."""
    return success_response(data=data, message=message, status_code=201)


def no_content_response():
    """
    Respuesta 204 No Content (para eliminaciones exitosas).
    Por convención REST, DELETE exitoso devuelve 204 sin cuerpo.
    """
    return '', 204




"""
Helper para estandarizar respuestas JSON de la API.

¿Por qué estandarizar respuestas?
Una API profesional siempre devuelve respuestas con la misma
estructura. Esto facilita que el frontend las procese de forma
predecible. Un cliente nunca debería adivinar el formato.

Estructura estándar que usaremos:
{
    "success": true/false,
    "message": "Descripción legible",
    "data": { ... },        # Solo en respuestas exitosas
    "errors": [ ... ],      # Solo en respuestas con error
    "meta": { ... }         # Metadata opcional (paginación, etc.)
}
"""