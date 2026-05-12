from typing import Optional, List
from sqlalchemy import or_, and_
from app.repositories.base_repository import BaseRepository
from app.models.movie import Movie
from app.utils.pagination import paginate_query


class MovieRepository(BaseRepository[Movie]):
    """
    Repositorio con operaciones de acceso a datos para películas.
    Hereda las operaciones CRUD básicas del BaseRepository.
    """
    
    def __init__(self):
        super().__init__(Movie)
    
    def find_by_id_active(self, movie_id: int) -> Optional[Movie]:
        """
        Busca una película activa por ID.
        Solo devuelve películas activas (soft delete pattern).
        """
        return Movie.query.filter(
            and_(Movie.id == movie_id, Movie.is_active == True)
        ).first()
    
    def find_all_paginated(
        self,
        page: int,
        per_page: int,
        search: Optional[str] = None,
        genre: Optional[str] = None,
        rating: Optional[str] = None,
        active_only: bool = True
    ) -> dict:
        """
        Lista películas con paginación y filtros opcionales.
        
        Args:
            page: Número de página
            per_page: Items por página
            search: Buscar en título o director
            genre: Filtrar por género
            rating: Filtrar por clasificación
            active_only: Solo películas activas
        
        Returns:
            dict con 'items' (lista de películas) y 'meta' (paginación)
        """
        # Construimos la query base
        query = Movie.query
        
        # Aplicamos filtros condicionalmente
        if active_only:
            query = query.filter(Movie.is_active == True)
        
        # Búsqueda de texto en título o director
        # ILIKE = case-insensitive LIKE en PostgreSQL
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Movie.title.ilike(search_term),
                    Movie.director.ilike(search_term)
                )
            )
        
        if genre:
            # Busca si el género está contenido en el campo genre
            query = query.filter(Movie.genre.ilike(f"%{genre}%"))
        
        if rating:
            query = query.filter(Movie.rating == rating.upper())
        
        # Ordenar por más recientes primero
        query = query.order_by(Movie.created_at.desc())
        
        return paginate_query(query, page, per_page)
    
    def find_by_title(self, title: str) -> Optional[Movie]:
        """Busca una película por título exacto (case-insensitive)."""
        return Movie.query.filter(
            Movie.title.ilike(title)
        ).first()
    
    def exists_by_title(self, title: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si ya existe una película con ese título.
        
        exclude_id: Al actualizar, excluir la propia película de la búsqueda
        """
        query = Movie.query.filter(Movie.title.ilike(title))
        if exclude_id:
            query = query.filter(Movie.id != exclude_id)
        return query.first() is not None