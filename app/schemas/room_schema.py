from marshmallow import (
    Schema, fields, validate, validates, validates_schema, ValidationError
)

class RoomCreateSchema(Schema):

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error='The name must be between 1 and 100 characters long')
    )

    # Filas de la sala (A, B, C...) — cada fila es una letra del abecedario
    # Máximo 26 filas = 26 letras del alfabeto inglés
    rows = fields.Int(
        required=True,
        validate=validate.Range(
            min=1, max=26,
            error='The rows must be between 1 and 26'
        )
    )

    # Asientos por fila (columnas)
    seats_per_row = fields.Int(
        required=True,
        validate=validate.Range(
            min=1, max=50,
            error='The number of seats per row must be between 1 and 50.'
        )
    )

    # Tipo de sala
    room_type = fields.Str(
        load_default='standard',
        validate=validate.OneOf(
            ['standard', 'vip', 'imax', '3d', '4dx'],
            error='Invalid room type. Options: standard, VIP, IMAX, 3D, 4DX'
        )
    )

    @validates('name')
    def validate_name_not_blank(self, value):
        if not value.strip():
            raise ValidationError('The name of the room cannot just be spaces')

    @validates_schema
    def validate_capacity(self, data, **kwargs):

        rows = data.get('rows', 0)
        seats_per_row = data.get('seats_per_row', 0)

        if rows and seats_per_row:
            total = rows * seats_per_row
            if total > 1000:
                raise ValidationError(
                    f'The room would have {total} seats, which exceeds the maximum of 1000. '
                    f'Reduce the number of rows or seats per row.'
                )
            if total < 10:
                raise ValidationError(
                    f'The room would have {total} seats. '
                    f'A room must have at least 10 seats.'
                )


class RoomUpdateSchema(Schema):

    name      = fields.Str(validate=validate.Length(min=1, max=100))
    room_type = fields.Str(
        validate=validate.OneOf(['standard', 'vip', 'imax', '3d', '4dx'])
    )
    is_active = fields.Bool()

    @validates('name')
    def validate_name_not_blank(self, value):
        if not value.strip():
            raise ValidationError('The name cannot be just spaces.')


class RoomResponseSchema(Schema):

    id            = fields.Int()
    name          = fields.Str()
    total_seats   = fields.Int()
    rows          = fields.Int()
    seats_per_row = fields.Int()
    room_type     = fields.Str()
    is_active     = fields.Bool()
    created_at    = fields.DateTime(format='iso')
    updated_at    = fields.DateTime(format='iso')


class RoomDetailSchema(RoomResponseSchema):

    # Cuántas funciones tiene programadas
    upcoming_screenings_count = fields.Method('get_upcoming_count')

    def get_upcoming_count(self, room):

        from datetime import datetime, timezone
        return room.screenings.filter(
            # Importamos aquí para evitar importación circular
            __import__(
                'app.models.screening',
                fromlist=['Screening']
            ).Screening.start_time > datetime.now(timezone.utc)
        ).count()


# ── Instancias singleton ──────────────────────────────────────────────────────

room_create_schema  = RoomCreateSchema()
room_update_schema  = RoomUpdateSchema()
room_response_schema  = RoomResponseSchema()
rooms_response_schema = RoomResponseSchema(many=True)
room_detail_schema  = RoomDetailSchema()