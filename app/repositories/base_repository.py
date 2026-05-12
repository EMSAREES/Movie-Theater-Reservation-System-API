

from typing import TypeVar, Generic, Type, Optional, List
from app import db

# TypeVar para tipado genérico — permite que BaseRepository
# trabaje con cualquier modelo sin perder información de tipo
T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Repositorio genérico con operaciones CRUD comunes.
    
    Uso:
        class MovieRepository(BaseRepository[Movie]):
            def __init__(self):
                super().__init__(Movie)
    
    Automáticamente tendrá: find_all, find_by_id, save, delete...
    """
    
    def __init__(self, model: Type[T]):
        """
        Args:
            model: La clase del modelo SQLAlchemy (ej: Movie, User)
        """
        self.model = model
    
    def find_by_id(self, id: int) -> Optional[T]:
        """
        Busca un registro por su clave primaria.
        
        Returns:
            El registro o None si no existe
        """
        return db.session.get(self.model, id)
    
    def find_all(self) -> List[T]:
        """Devuelve todos los registros de la tabla."""
        return self.model.query.all()
    
    def save(self, entity: T) -> T:
        """
        Guarda (INSERT o UPDATE) un registro.
        
        SQLAlchemy detecta automáticamente si es INSERT o UPDATE
        basado en si el objeto ya tiene id o no.
        
        Args:
            entity: El objeto modelo a guardar
        
        Returns:
            El mismo objeto con id asignado (si era nuevo)
        """
        db.session.add(entity)
        db.session.flush()  # Ejecuta el SQL pero NO hace commit
        # flush() es importante: asigna el id sin confirmar la transacción
        # El commit lo hace el controlador (o un context manager)
        return entity
    
    def delete(self, entity: T) -> None:
        """Elimina un registro de la base de datos."""
        db.session.delete(entity)
        db.session.flush()
    
    def commit(self) -> None:
        """
        Confirma la transacción actual.
        
        ¿Por qué tener commit() en el repo?
        Porque a veces una operación de negocio requiere
        múltiples saves() antes de hacer commit.
        El servicio controla cuándo confirmar.
        """
        db.session.commit()
    
    def rollback(self) -> None:
        """Revierte la transacción en caso de error."""
        db.session.rollback()
    
    def count(self) -> int:
        """Cuenta el total de registros."""
        return self.model.query.count()
    

# app/repositories/base_repository.py
"""
Repositorio Base — Operaciones CRUD genéricas.

¿Qué es el patrón Repository?
Es una capa de abstracción sobre la base de datos.
Concentra TODA la lógica de acceso a datos en un lugar.

Ventajas:
1. Los servicios no saben NADA de SQLAlchemy
2. Si cambias de PostgreSQL a MongoDB, solo cambias los repos
3. Los repos son fáciles de testear con mocks
4. Evitas duplicar queries en múltiples lugares

En vez de que el servicio haga:
    movie = Movie.query.filter_by(id=id, is_active=True).first()

El servicio hace:
    movie = self.movie_repo.find_by_id(id)

¿Ves la diferencia? El servicio no sabe de SQLAlchemy.
"""