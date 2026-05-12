from flask import request
from marshmallow import ValidationError

from app.services.movie_service import MovieService
from app.schemas.movie_schema import (
    movie_create_schema,
    movie_update_schema,
    movie_response_schema,
    movies_response_schema
)
from app.utils.response_helper import (
    success_response, error_response, created_response, no_content_response
)
from app.utils.pagination import get_pagination_params
from app.exceptions.app_exceptions import AppException


class MovieController:
    """
    Controlador con los handlers para cada endpoint de películas.
    Cada método maneja un endpoint específico.
    """
    
    def __init__(self):
        self.service = MovieService()
    
    def get_all(self):
        """
        GET /api/v1/movies
        Lista películas con paginación y filtros opcionales.
        
        Query params:
            page, per_page: paginación
            search: búsqueda por título/director
            genre: filtrar por género
            rating: filtrar por clasificación
        """
        page, per_page = get_pagination_params()
        
        # request.args es un diccionario con los query parameters de la URL
        search = request.args.get('search')
        genre = request.args.get('genre')
        rating = request.args.get('rating')
        
        result = self.service.get_all_movies(
            page=page,
            per_page=per_page,
            search=search,
            genre=genre,
            rating=rating
        )
        
        return success_response(
            data=movies_response_schema.dump(result['items']),
            message="Películas obtenidas exitosamente",
            meta=result['meta']
        )
    
    def get_by_id(self, movie_id: int):
        """
        GET /api/v1/movies/<movie_id>
        Obtiene el detalle de una película específica.
        """
        try:
            movie = self.service.get_movie_by_id(movie_id)
            return success_response(
                data=movie_response_schema.dump(movie),
                message="Película obtenida exitosamente"
            )
        except AppException as e:
            return error_response(e.message, e.status_code)
    
    def create(self):
        """
        POST /api/v1/movies
        Crea una nueva película.
        
        Body: JSON con datos de la película
        """
        try:
            # 1. Obtener JSON del body del request
            json_data = request.get_json()
            if not json_data:
                return error_response("Se requiere un body JSON", 400)
            
            # 2. Validar y deserializar con el schema
            # Si hay errores de validación, marshmallow lanza ValidationError
            validated_data = movie_create_schema.load(json_data)
            
            # 3. Llamar al servicio
            movie = self.service.create_movie(validated_data)
            
            # 4. Serializar y devolver
            return created_response(
                data=movie_response_schema.dump(movie),
                message="Película creada exitosamente"
            )
        
        except ValidationError as e:
            # Errores de validación del schema (campos inválidos, faltantes)
            return error_response(
                message="Datos de entrada inválidos",
                status_code=422,
                errors=_flatten_validation_errors(e.messages)
            )
        except AppException as e:
            return error_response(e.message, e.status_code)
    
    def update(self, movie_id: int):
        """
        PUT /api/v1/movies/<movie_id>
        Actualiza una película existente.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                return error_response("Se requiere un body JSON", 400)
            
            validated_data = movie_update_schema.load(json_data)
            movie = self.service.update_movie(movie_id, validated_data)
            
            return success_response(
                data=movie_response_schema.dump(movie),
                message="Película actualizada exitosamente"
            )
        
        except ValidationError as e:
            return error_response(
                message="Datos de entrada inválidos",
                status_code=422,
                errors=_flatten_validation_errors(e.messages)
            )
        except AppException as e:
            return error_response(e.message, e.status_code)
    
    def delete(self, movie_id: int):
        """
        DELETE /api/v1/movies/<movie_id>
        Elimina (soft delete) una película.
        """
        try:
            self.service.delete_movie(movie_id)
            return no_content_response()
        except AppException as e:
            return error_response(e.message, e.status_code)


def _flatten_validation_errors(errors: dict) -> list:
    """
    Convierte el dict de errores de Marshmallow a lista plana.
    
    Marshmallow devuelve: {'title': ['El campo es requerido']}
    Nosotros devolvemos: ['title: El campo es requerido']
    """
    flat_errors = []
    for field, messages in errors.items():
        if isinstance(messages, list):
            for msg in messages:
                flat_errors.append(f"{field}: {msg}")
        elif isinstance(messages, dict):
            # Errores en campos anidados
            for nested_field, nested_msgs in messages.items():
                for msg in nested_msgs:
                    flat_errors.append(f"{field}.{nested_field}: {msg}")
    return flat_errors


"""
Controlador de Películas.

¿Qué hace el controlador?
1. Recibe el request HTTP
2. Extrae y valida los datos de entrada (usando schemas)
3. Llama al servicio apropiado
4. Captura excepciones y las convierte en respuestas HTTP
5. Serializa el resultado y lo devuelve

El controlador NO contiene lógica de negocio.
Si un controlador crece demasiado, es señal de que
la lógica debería estar en el servicio.
"""