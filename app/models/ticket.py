import uuid
from datetime import datetime, timezone
from app import db

class Ticket(db.Model):

    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Código único legible para el cliente (ej: "CIN-A1B2C3D4")
    # UUID hace casi imposible que alguien adivine un código de ticket
    ticket_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        default=lambda: f"CIN-{str(uuid.uuid4()).upper()[:8]}"
    )

    # ── Claves Foráneas ───────────────────────────────────────────────────────

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )
    
    screening_id = db.Column(
        db.Integer,
        db.ForeignKey('screenings.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )

    # ── Datos del asiento ─────────────────────────────────────────────────────
    
    # Número/código del asiento: "A1", "B5", "C10"
    # La lógica de asignación la maneja el servicio
    seat_number = db.Column(db.String(10), nullable=False)
    
    # Fila (A, B, C...) y número de asiento (1, 2, 3...)
    seat_row = db.Column(db.String(5), nullable=False)
    seat_column = db.Column(db.Integer, nullable=False)

    # ── Datos del precio ──────────────────────────────────────────────────────

    # Precio al momento de la compra (puede diferir del precio actual)
    # Siempre guardar el precio histórico en transacciones financieras
    price_paid = db.Column(db.Numeric(10, 2), nullable=False)

    # 'reserved' → reservado, 'paid' → pagado, 'cancelled' → cancelado
    status = db.Column(db.String(20), nullable=False, default='reserved')

    # Cuándo se hizo la reserva
    purchased_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Cuándo se canceló (si aplica)
    cancelled_at = db.Column(db.DateTime(timezone=True), nullable=True)

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

    # El mismo asiento NO puede venderse dos veces para la misma función.
    # Esta restricción la garantiza la BASE DE DATOS (no solo el código).

    __table_args__ = (
        db.UniqueConstraint(
            'screening_id',
            'seat_number',
            name='uq_screening_seat'
        ),
    )

    def cancel(self) -> None:
        """Cancela el ticket y registra la fecha de cancelación."""
        self.status = 'cancelled'
        self.cancelled_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f'<Ticket {self.ticket_code}: User={self.user_id} Seat={self.seat_number}>'