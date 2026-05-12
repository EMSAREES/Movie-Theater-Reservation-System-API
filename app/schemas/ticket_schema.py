from marshmallow import Schema, fields, validate, validates, ValidationError

class TicketCreateSchema(Schema):

    screening_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="Invalid function ID")
    )
    
    seat_row = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=5)
    )
    
    seat_column = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="The seat number must be positive")
    )
    
    @validates('seat_row')
    def validate_seat_row(self, value):
        """La fila debe ser una letra mayúscula válida."""
        if not value.upper().isalpha():
            raise ValidationError("The row must be a letter (A, B, C...)")
        
class TicketResponseSchema(Schema):
    
    id = fields.Int()
    ticket_code = fields.Str()
    user_id = fields.Int()
    screening_id = fields.Int()
    seat_number = fields.Str()
    seat_row = fields.Str()
    seat_column = fields.Int()
    price_paid = fields.Decimal(as_string=True)  # Decimal como string evita errores de flotante
    status = fields.Str()
    purchased_at = fields.DateTime(format='iso')
    cancelled_at = fields.DateTime(format='iso', dump_default=None)
    
    # Información anidada de la función
    screening = fields.Nested(lambda: ScreeningBasicSchema())


class ScreeningBasicSchema(Schema):
    
    id = fields.Int()
    start_time = fields.DateTime(format='iso')
    movie_title = fields.Method('get_movie_title')
    room_name = fields.Method('get_room_name')
    
    def get_movie_title(self, obj):
        return obj.movie.title if obj.movie else None
    
    def get_room_name(self, obj):
        return obj.room.name if obj.room else None


# Schemas de Usuario
class UserRegisterSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8, error="The password must be at least 8 characters long"),
        load_only=True  # Solo en entrada, NUNCA en respuestas
    )

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

class UserResponseSchema(Schema):
    id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    full_name = fields.Str()
    email = fields.Str()
    role = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime(format='iso')


# Schemas de Sala
class RoomCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    rows = fields.Int(required=True, validate=validate.Range(min=1, max=50))
    seats_per_row = fields.Int(required=True, validate=validate.Range(min=1, max=50))
    room_type = fields.Str(
        load_default='standard',
        validate=validate.OneOf(['standard', 'vip', 'imax', '3d', '4dx'])
    )

class RoomResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    total_seats = fields.Int()
    rows = fields.Int()
    seats_per_row = fields.Int()
    room_type = fields.Str()
    is_active = fields.Bool()


# Schemas de Función
class ScreeningCreateSchema(Schema):
    movie_id = fields.Int(required=True, validate=validate.Range(min=1))
    room_id = fields.Int(required=True, validate=validate.Range(min=1))
    start_time = fields.DateTime(required=True, format='iso')
    price = fields.Decimal(
        required=True,
        validate=validate.Range(min=0.01, error="The price must be greater than 0")
    )
    language = fields.Str(load_default='español')
    format = fields.Str(
        load_default='2D',
        validate=validate.OneOf(['2D', '3D', 'IMAX', '4DX'])
    )

class ScreeningResponseSchema(Schema):
    id = fields.Int()
    movie_id = fields.Int()
    room_id = fields.Int()
    start_time = fields.DateTime(format='iso')
    end_time = fields.DateTime(format='iso')
    price = fields.Decimal(as_string=True)
    language = fields.Str()
    format = fields.Str()
    status = fields.Str()
    sold_seats = fields.Int()
    available_seats = fields.Int()
    is_full = fields.Bool()
    movie = fields.Nested(lambda: MovieBasicSchema())
    room = fields.Nested(lambda: RoomBasicSchema())

class MovieBasicSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    duration_minutes = fields.Int()
    rating = fields.Str()

class RoomBasicSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    total_seats = fields.Int()



ticket_create_schema = TicketCreateSchema()
ticket_response_schema = TicketResponseSchema()
tickets_response_schema = TicketResponseSchema(many=True)

user_register_schema = UserRegisterSchema()
user_login_schema = UserLoginSchema()
user_response_schema = UserResponseSchema()

room_create_schema = RoomCreateSchema()
room_response_schema = RoomResponseSchema()
rooms_response_schema = RoomResponseSchema(many=True)

screening_create_schema = ScreeningCreateSchema()
screening_response_schema = ScreeningResponseSchema()
screenings_response_schema = ScreeningResponseSchema(many=True)

# Schema de actualización de función (campos opcionales)
class ScreeningUpdateSchema(Schema):
    price    = fields.Decimal(validate=validate.Range(min=0.01))
    language = fields.Str(validate=validate.Length(min=1, max=50))
    format   = fields.Str(validate=validate.OneOf(['2D', '3D', 'IMAX', '4DX']))
    status   = fields.Str(validate=validate.OneOf(
        ['scheduled', 'ongoing', 'finished', 'cancelled']
    ))
