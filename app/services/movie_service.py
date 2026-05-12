from typing import Optional
from app.repositories.movie_repository import MovieRepository
from app.exceptions.app_exceptions import (
    MovieNotFoundException,
    ConflictException
)


class MovieService:
    """
    Servicio con toda la lógica de negocio para películas.
    """
    
    def __init__(self):
        # Inyección de dependencias manual
        # En frameworks más avanzados usarías un contenedor DI
        self.repo = MovieRepository()
    
    def get_all_movies(
        self,
        page: int,
        per_page: int,
        search: Optional[str] = None,
        genre: Optional[str] = None,
        rating: Optional[str] = None
    ) -> dict:
        """
        Lista películas con paginación y filtros.
        Delega la query al repositorio.
        """
        return self.repo.find_all_paginated(
            page=page,
            per_page=per_page,
            search=search,
            genre=genre,
            rating=rating
        )
    
    def get_movie_by_id(self, movie_id: int):
        """
        Obtiene una película por ID.
        Lanza excepción si no existe (el controlador la captura).
        """
        movie = self.repo.find_by_id_active(movie_id)
        if not movie:
            raise MovieNotFoundException(movie_id)
        return movie
    
    def create_movie(self, data: dict):
        """
        Crea una nueva película.
        
        Reglas de negocio:
        - No pueden existir dos películas con el mismo título
        
        Args:
            data: Diccionario validado por el schema
        
        Returns:
            La película creada con su id asignado
        """
        from app.models.movie import Movie
        
        # Regla de negocio: título único
        if self.repo.exists_by_title(data['title']):
            raise ConflictException(
                f"Ya existe una película con el título '{data['title']}'"
            )
        
        # Crear el objeto modelo con los datos del schema
        movie = Movie(**data)
        
        # Guardar en BD
        self.repo.save(movie)
        self.repo.commit()
        
        return movie
    
    def update_movie(self, movie_id: int, data: dict):
        """
        Actualiza una película existente.
        Solo actualiza los campos que vienen en data.
        """
        movie = self.get_movie_by_id(movie_id)
        
        # Verificar título único si se está cambiando
        if 'title' in data and data['title'].lower() != movie.title.lower():
            if self.repo.exists_by_title(data['title'], exclude_id=movie_id):
                raise ConflictException(
                    f"Ya existe una película con el título '{data['title']}'"
                )
        
        # Actualizar solo los campos proporcionados
        # setattr(obj, campo, valor) es equivalente a obj.campo = valor
        for field, value in data.items():
            setattr(movie, field, value)
        
        self.repo.save(movie)
        self.repo.commit()
        
        return movie
    
    def delete_movie(self, movie_id: int) -> None:
        """
        Soft delete: marca como inactiva en vez de borrar.
        
        ¿Por qué soft delete?
        Si borramos físicamente una película que tiene funciones
        y tickets vendidos, perdemos el historial.
        Con soft delete preservamos la integridad referencial.
        """
        movie = self.get_movie_by_id(movie_id)
        movie.is_active = False
        self.repo.save(movie)
        self.repo.commit()



"""
Servicio de Películas — Lógica de negocio.

¿Qué va aquí?
La lógica de NEGOCIO, no de base de datos ni de HTTP.
Preguntas que responde el servicio:
- ¿Se puede crear esta película? (¿ya existe una con ese título?)
- ¿Qué pasa si se elimina una película con funciones activas?
- ¿Qué validaciones de negocio aplican?

El servicio NO sabe de:
- Requests HTTP (eso es el controlador)
- SQLAlchemy queries (eso es el repositorio)

Solamente habla con el repositorio y aplica reglas de negocio.
"""