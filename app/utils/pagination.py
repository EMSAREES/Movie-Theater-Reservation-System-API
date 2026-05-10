from flask import request
from typing import Any
from app.config.settings import BaseConfig


def get_pagination_params() -> tuple[int, int]:
    """
    Extrae y valida los parámetros de paginación del request.
    
    Lee ?page=X&per_page=Y de la URL.
    Si no vienen, usa valores por defecto.
    
    Returns:
        Tuple[page, per_page]: Número de página y tamaño de página
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', BaseConfig.DEFAULT_PAGE_SIZE))
    except (ValueError, TypeError):
        # Si los parámetros no son números válidos, usar defaults
        page = 1
        per_page = BaseConfig.DEFAULT_PAGE_SIZE
    
    # Validaciones de seguridad
    # Evitar páginas negativas o cero
    page = max(1, page)
    
    # Limitar el tamaño máximo de página para proteger el servidor
    per_page = min(max(1, per_page), BaseConfig.MAX_PAGE_SIZE)
    
    return page, per_page


def paginate_query(query, page: int, per_page: int) -> dict:
    """
    Ejecuta una query de SQLAlchemy con paginación.
    
    Args:
        query: Query de SQLAlchemy (antes de ejecutar)
        page: Número de página actual
        per_page: Cantidad de items por página
    
    Returns:
        dict con los items y metadata de paginación
    
    Ejemplo de uso en un repositorio:
        query = Movie.query.filter_by(active=True)
        return paginate_query(query, page=1, per_page=10)
    """
    # SQLAlchemy paginate() hace el LIMIT/OFFSET automáticamente
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False  # No lanzar error si la página está vacía
    )
    
    return {
        "items": pagination.items,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "next_page": page + 1 if pagination.has_next else None,
            "prev_page": page - 1 if pagination.has_prev else None
        }
    }




"""
Helper para paginación de resultados.

¿Por qué paginar?
Imagina que la BD tiene 50,000 películas.
Devolver todo de una vez sería:
- Lento (mucha transferencia de datos)
- Costoso (memoria del servidor)
- Inutilizable para el cliente

La paginación devuelve "páginas" de resultados:
GET /api/v1/movies?page=1&per_page=10
"""