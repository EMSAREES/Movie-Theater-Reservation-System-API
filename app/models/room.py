from datetime import datetime, timezone
from app import db

class Room(db.Model):

    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Nombre descriptivo: "Sala 1", "Sala VIP", "IMAX"
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    # Capacidad total de asientos
    total_seats = db.Column(db.Integer, nullable=False)
    
    # Filas de asientos (ej: 10 filas × 15 asientos = 150 total)
    rows = db.Column(db.Integer, nullable=False)
    seats_per_row = db.Column(db.Integer, nullable=False)
    
    # Tipo de sala para categorización
    # 'standard', 'vip', 'imax', '3d', '4dx'
    room_type = db.Column(db.String(50), nullable=False, default='standard')
    
    # ¿Está operativa?
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
    screenings = db.relationship(
        'Screening',
        backref='room',
        lazy='dynamic'
    )
    
    def __repr__(self) -> str:
        return f'<Room {self.id}: {self.name} ({self.total_seats} seats)>'
