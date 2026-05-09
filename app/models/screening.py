from datetime import datetime, timezone
from app import db

class Screening(db.Model):

    __tablename__ = 'screenings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ── Claves Foráneas (Foreign Keys) ────────────────────────────────────────
    #
    # ¿Qué es una Foreign Key?
    # Es una columna que referencia la clave primaria de otra tabla.
    # Establece y ENFORZA la relación entre tablas a nivel de BD.
    # Si intentas insertar un movie_id que no existe, PostgreSQL lo rechaza.
    #
    # Esto garantiza integridad referencial: no pueden existir funciones
    # huérfanas que apunten a películas o salas inexistentes.
    movie_id = db.Column(
        db.Integer,
        db.ForeignKey('movies.id', ondelete='RESTRICT'),
        # ondelete='RESTRICT': No permite borrar una película si tiene funciones
        nullable=False,
        index=True
    )

    room_id = db.Column(
        db.Integer,
        db.ForeignKey('rooms.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )

    # ── Columnas propias ──────────────────────────────────────────────────────

    # Cuándo empieza la función
    start_time = db.Column(db.DateTime(timezone=True), nullable=False, index=True)

    # Cuándo termina (calculado: start_time + duración de la película)
    end_time = db.Column(db.DateTime(timezone=True), nullable=False)

    # Precio en formato decimal: 12.50
    # Numeric(10, 2) = hasta 10 dígitos totales, 2 decimales
    price = db.Column(db.Numeric(10, 2), nullable=False)

    # Idioma de la proyección (puede diferir del idioma original)
    # 'original', 'dobladο', 'subtitulado'
    language = db.Column(db.String(50), nullable=False, default='español')

    # Formato especial: '2D', '3D', 'IMAX', '4DX'
    format = db.Column(db.String(20), nullable=False, default='2D')

    # Estado de la función
    # 'scheduled' → programada, 'ongoing' → en curso,
    # 'finished' → terminada, 'cancelled' → cancelada
    status = db.Column(db.String(20), nullable=False, default='scheduled')

    # Asientos ya vendidos (desnormalización controlada para rendimiento)
    # Lo actualizamos cada vez que se vende/cancela un ticket
    sold_seats = db.Column(db.Integer, nullable=False, default=0)

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

    # ── Restricción única compuesta ───────────────────────────────────────────

    # No puede haber dos funciones en la misma sala al mismo tiempo.
    # UniqueConstraint a nivel de BD (más robusto que validación en código)

    __table_args__ = (
        db.UniqueConstraint(
            'room_id',
            'start_time',
            name='uq_room_start_time'
        ),
    )

    # ── Relaciones ────────────────────────────────────────────────────────────

    tickets = db.relationship(
        'Ticket',
        backref='screening',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # ── Propiedades calculadas ────────────────────────────────────────────────

    @property
    def available_seats(self) -> int:
        """Cuántos asientos quedan disponibles."""
        return self.room.total_seats - self.sold_seats

    @property
    def is_full(self) -> bool:
        """¿Está llena la función?"""
        return self.available_seats <= 0

    @property
    def is_available_for_booking(self) -> bool:
        """¿Se pueden comprar tickets para esta función?"""
        now = datetime.now(timezone.utc)
        return (
            self.status == 'scheduled'
            and self.start_time > now
            and not self.is_full
        )

    def __repr__(self) -> str:
        return f'<Screening {self.id}: Movie={self.movie_id} Room={self.room_id} at {self.start_time}>'


"""
Modelo de Función (Screening).

Una función es la combinación de:
- Una película específica
- Una sala específica
- Una fecha y hora específica
- Un precio de entrada

Es la entidad central del sistema: los tickets se venden para funciones.
"""