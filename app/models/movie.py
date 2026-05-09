from datetime import datetime, timezone
from app import db

class Movie(db.Model):

    __tablename__ = 'movies'

    # ── Columnas ──────────────────────────────────────────────────────────────

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    title = db.Column(db.String(255), nullable=False, index=True)
    
    # Text para descripciones largas (sin límite fijo)
    description = db.Column(db.Text, nullable=True)
    
    # Duración en minutos — Integer simple
    duration_minutes = db.Column(db.Integer, nullable=False)
    
    # Géneros como string separado por comas: "Acción,Aventura,Sci-Fi"
    # En un sistema más complejo usaríamos una tabla genres con relación M:N
    genre = db.Column(db.String(255), nullable=False)
    
    # Clasificación: G, PG, PG-13, R, NC-17
    rating = db.Column(db.String(10), nullable=False, default='PG')
    
    # URL del poster/imagen
    poster_url = db.Column(db.String(500), nullable=True)
    
    # Director de la película
    director = db.Column(db.String(200), nullable=True)
    
    # Fecha de estreno
    release_date = db.Column(db.Date, nullable=True)
    
    # Idioma original
    language = db.Column(db.String(50), nullable=False, default='Español')
    
    # ¿Está activa/disponible para funciones?
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # ── Relaciones ────────────────────────────────────────────────────────────
    
    # Una película puede tener muchas funciones (screenings)
    screenings = db.relationship(
        'Screening',
        backref='movie',
        lazy='dynamic'
    )

    # ── Propiedades calculadas ────────────────────────────────────────────────
    @property
    def duration_formatted(self) -> str:
        """
        Formatea duración: 125 minutos → "2h 5min"
        """
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}min" if minutes > 0 else f"{hours}h"
        return f"{minutes}min"
    
    def __repr__(self) -> str:
        return f'<Movie {self.id}: {self.title}>'