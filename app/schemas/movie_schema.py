from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from datetime import date

class MovieCreateSchema(Schema):

    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255, error="The title must be between 1 and 255 characters long")
    )

    description = fields.Str(
        load_default=None  # Valor por defecto si no viene en el request
    )

    duration_minutes = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=600, error="The duration should be between 1 and 600 minutes")
    )

    genre = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255)
    )

    rating = fields.Str(
        load_default='PG',
        validate=validate.OneOf(
            ['G', 'PG', 'PG-13', 'R', 'NC-17'],
            error="Invalid classification. Options: G, PG, PG-13, R, NC-17"
        )
    )

    poster_url = fields.Url(load_default=None, allow_none=True)
    
    director = fields.Str(load_default=None, validate=validate.Length(max=200))
    
    release_date = fields.Date(load_default=None, allow_none=True)
    
    language = fields.Str(load_default='Español', validate=validate.Length(max=50))

    @validates('title')
    def validate_title_not_empty(self, value):
        """Validación personalizada: el título no puede ser solo espacios."""
        if not value.strip():
            raise ValidationError("The title cannot be empty or consist only of spaces.")
        

class MovieUpdateSchema(Schema):
    
    title = fields.Str(validate=validate.Length(min=1, max=255))

    description = fields.Str(allow_none=True)

    duration_minutes = fields.Int(validate=validate.Range(min=1, max=600))

    genre = fields.Str(validate=validate.Length(min=1, max=255))

    rating = fields.Str(validate=validate.OneOf(['G', 'PG', 'PG-13', 'R', 'NC-17']))

    poster_url = fields.Url(allow_none=True)

    director = fields.Str(allow_none=True, validate=validate.Length(max=200))

    release_date = fields.Date(allow_none=True)

    language = fields.Str(validate=validate.Length(max=50))

    is_active = fields.Bool()


class MovieResponseSchema(Schema):
    id = fields.Int(dump_default=None)
    title = fields.Str()
    description = fields.Str(dump_default=None)
    duration_minutes = fields.Int()
    duration_formatted = fields.Str()  # Propiedad calculada del modelo
    genre = fields.Str()
    rating = fields.Str()
    poster_url = fields.Str(dump_default=None)
    director = fields.Str(dump_default=None)
    release_date = fields.Date(dump_default=None)
    language = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime(format='iso')
    updated_at = fields.DateTime(format='iso')



movie_create_schema = MovieCreateSchema()
movie_update_schema = MovieUpdateSchema()
movie_response_schema = MovieResponseSchema()
movies_response_schema = MovieResponseSchema(many=True)

"""
Schemas de Película con Marshmallow.

¿Qué es un Schema/DTO?
DTO = Data Transfer Object

Es un "contrato" que define:
1. Qué campos acepta la API (input) y cuáles devuelve (output)
2. Qué tipos de datos son válidos
3. Qué campos son obligatorios
4. Qué validaciones aplicar

Sin schemas: Un usuario podría enviar cualquier basura a la API
Con schemas: Solo datos válidos y esperados pasan al servicio

Marshmallow nos da:
- Serialización: Objeto Python → JSON
- Deserialización: JSON → Objeto Python validado
- Validación automática
"""