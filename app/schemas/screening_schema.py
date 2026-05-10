from marshmallow import (
    Schema, fields, validate, validates, validates_schema,
    ValidationError, pre_load
)
from datetime import datetime, timezone


class MovieNestedSchema(Schema):
    """
    Info de película para incrustar dentro de respuestas de función.
    Solo los campos que el cliente necesita para mostrar la función.
    """
    id               = fields.Int()
    title            = fields.Str()
    duration_minutes = fields.Int()
    duration_formatted = fields.Str()   # "2h 5min"
    genre            = fields.Str()
    rating           = fields.Str()
    poster_url       = fields.Str(dump_default=None)
    director         = fields.Str(dump_default=None)


class RoomNestedSchema(Schema):
    """Info de sala para incrustar dentro de respuestas de función."""
    id            = fields.Int()
    name          = fields.Str()
    total_seats   = fields.Int()
    rows          = fields.Int()
    seats_per_row = fields.Int()
    room_type     = fields.Str()


# ── Schemas principales ───────────────────────────────────────────────────────

class ScreeningCreateSchema(Schema):
    """Schema para POST /api/v1/screenings"""

    movie_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error='Invalid movie ID')
    )
    room_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error='Invalid room ID')
    )

    # La fecha y hora de inicio en formato ISO 8601
    # Ejemplo: "2025-08-15T20:00:00" o "2025-08-15T20:00:00+06:00"
    start_time = fields.DateTime(
        required=True,
        format='iso',
        error_messages={'required': 'The start date and time is required'}
    )

    # Precio con hasta 2 decimales
    price = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(
            min=0.01,
            error='The price must be greater than $0.00'
        )
    )

    language = fields.Str(
        load_default='español',
        validate=validate.Length(max=50)
    )

    format = fields.Str(
        load_default='2D',
        validate=validate.OneOf(
            ['2D', '3D', 'IMAX', '4DX'],
            error='Invalid format. Options: 2D, 3D, IMAX, 4DX'
        )
    )

    @validates('start_time')
    def validate_start_time_future(self, value):
        """
        La función no puede programarse en el pasado.
        Validamos que start_time sea al menos 30 minutos en el futuro
        para dar tiempo a la operación.
        """
        from datetime import timedelta

        # Aseguramos que el datetime tenga zona horaria para comparar
        if value.tzinfo is None:
            # Si viene sin timezone, asumimos UTC
            value = value.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        min_future = now + timedelta(minutes=30)

        if value <= now:
            raise ValidationError(
                'The function must be programmed in the future.'
            )

        if value < min_future:
            raise ValidationError(
                'The performance must be scheduled at least 30 minutes in advance.'
            )


class ScreeningUpdateSchema(Schema):
    """
    NO permitimos cambiar la película o la sala de una función
    que ya existe (eso requeriría cancelarla y crear una nueva).
    Solo permitimos ajustar precio, idioma, formato y estado.
    """

    price    = fields.Decimal(places=2, validate=validate.Range(min=0.01))
    language = fields.Str(validate=validate.Length(max=50))
    format   = fields.Str(validate=validate.OneOf(['2D', '3D', 'IMAX', '4DX']))
    status   = fields.Str(
        validate=validate.OneOf(
            ['scheduled', 'cancelled'],
            error='You can only change the status to "scheduled" or "cancelled".'
        )
    )

    @validates_schema
    def validate_at_least_one_field(self, data, **kwargs):
        """
        Una actualización vacía no tiene sentido.
        Requiere al menos un campo.
        """
        if not data:
            raise ValidationError(
                'You must submit at least one field to update'
            )


class ScreeningResponseSchema(Schema):
    """
    Schema de respuesta completo para una función.

    Incluye datos anidados de película y sala para que el frontend
    no tenga que hacer requests adicionales.

    available_seats e is_full son propiedades calculadas del modelo.
    is_available_for_booking combina status + tiempo + disponibilidad.
    """

    id         = fields.Int()
    movie_id   = fields.Int()
    room_id    = fields.Int()
    start_time = fields.DateTime(format='iso')
    end_time   = fields.DateTime(format='iso')

    # Decimal as_string=True evita problemas de precisión flotante
    # 95.50 en float puede ser 95.49999999... — como string siempre es "95.50"
    price      = fields.Decimal(as_string=True)

    language   = fields.Str()
    format     = fields.Str()
    status     = fields.Str()
    sold_seats = fields.Int()

    # Propiedades calculadas del modelo
    available_seats           = fields.Int()
    is_full                   = fields.Bool()
    is_available_for_booking  = fields.Bool()

    # Datos anidados — evitan que el cliente haga 2 requests más
    movie = fields.Nested(MovieNestedSchema)
    room  = fields.Nested(RoomNestedSchema)

    created_at = fields.DateTime(format='iso')
    updated_at = fields.DateTime(format='iso')


class ScreeningListResponseSchema(Schema):
    """
    Schema para listados de funciones.
    Versión más ligera: no incluye todos los datos anidados,
    solo lo necesario para mostrar una lista.
    """

    id         = fields.Int()
    start_time = fields.DateTime(format='iso')
    end_time   = fields.DateTime(format='iso')
    price      = fields.Decimal(as_string=True)
    language   = fields.Str()
    format     = fields.Str()
    status     = fields.Str()
    available_seats = fields.Int()
    is_full         = fields.Bool()

    # En el listado solo incluimos título de película y nombre de sala
    # para mantener la respuesta liviana
    movie = fields.Nested(MovieNestedSchema(only=('id', 'title', 'rating', 'poster_url')))
    room  = fields.Nested(RoomNestedSchema(only=('id', 'name', 'room_type')))


class SeatSchema(Schema):
    """
    Schema para un asiento individual en el mapa de asientos.
    Se usa dentro de ScreeningSeatsSchema.
    """

    seat_number = fields.Str()    # "A1", "B5", "C10"
    row         = fields.Str()    # "A", "B", "C"
    column      = fields.Int()    # 1, 2, 3...
    is_taken    = fields.Bool()   # True si ya fue vendido


class ScreeningSeatsSchema(Schema):
    """
    Schema para GET /api/v1/screenings/<id>/seats
    Devuelve el mapa completo de asientos de una función.
    """

    screening_id    = fields.Int()
    total_seats     = fields.Int()
    available_seats = fields.Int()
    sold_seats      = fields.Int()

    # Lista de todos los asientos con su estado
    seats = fields.List(fields.Nested(SeatSchema))


# ── Instancias singleton ──────────────────────────────────────────────────────

screening_create_schema    = ScreeningCreateSchema()
screening_update_schema    = ScreeningUpdateSchema()
screening_response_schema  = ScreeningResponseSchema()
screenings_response_schema = ScreeningListResponseSchema(many=True)
screening_seats_schema     = ScreeningSeatsSchema()