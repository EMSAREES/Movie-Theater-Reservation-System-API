from marshmallow import (
    Schema, fields, validate, validates, validates_schema,
    ValidationError, pre_load
)

class UserRegisterSchema(Schema):

    first_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error='The name must be between 1 and 100 characters long')
    )
    last_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error='The surname must be between 1 and 100 characters long')
    )
    email = fields.Email(
        required=True,
        error_messages={'required': 'The email is required', 'invalid': 'The email is not valid'}
    )
    password = fields.Str(
        required=True,
        load_only=True,   # Solo en input, NUNCA en output
        validate=validate.Length(min=8, error='The password must be at least 8 characters long')
    )
    # Campo opcional: confirmación de contraseña
    # También load_only porque es solo para validación, no se guarda
    password_confirm = fields.Str(load_only=True, load_default=None)

    # Campos opcionales del perfil
    phone = fields.Str(
        load_default=None,
        validate=validate.Length(max=20, error='The phone number cannot have more than 20 characters.')
    )

    @pre_load
    def normalize_email(self, data, **kwargs):
        """
        Normaliza el email a minúsculas antes de validar.
        pre_load se ejecuta ANTES de la validación de campos.
        Así evitamos que "Ana@Email.COM" y "ana@email.com"
        se traten como emails diferentes.
        """
        if 'email' in data and isinstance(data['email'], str):
            data['email'] = data['email'].lower().strip()
        return data

    @validates('first_name')
    def validate_first_name(self, value):
        """El nombre no puede ser solo espacios en blanco."""
        if not value.strip():
            raise ValidationError('The name cannot be just spaces.')

    @validates('last_name')
    def validate_last_name(self, value):
        if not value.strip():
            raise ValidationError('The surname cannot be just spaces.')

    @validates('password')
    def validate_password_strength(self, value):
        """
        Validación básica de fortaleza de contraseña.
        En producción podrías usar la librería `password-strength`.

        Reglas mínimas:
        - Al menos 8 caracteres (ya validado por Length)
        - Al menos un número
        - Al menos una letra
        """
        if not any(char.isdigit() for char in value):
            raise ValidationError('The password must contain at least one number')
        if not any(char.isalpha() for char in value):
            raise ValidationError('The password must contain at least one letter')

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """
        validates_schema se ejecuta después de validar los campos individuales.
        Aquí comparamos los dos campos de contraseña juntos.
        Solo validamos si password_confirm viene en el request.
        """
        password = data.get('password')
        password_confirm = data.get('password_confirm')

        if password_confirm is not None and password != password_confirm:
            raise ValidationError(
                {'password_confirm': ['The passwords do not match']}
            )


class UserLoginSchema(Schema):

    email = fields.Email(
        required=True,
        error_messages={'required': 'Email is mandatory'}
    )
    password = fields.Str(
        required=True,
        load_only=True,
        error_messages={'required': 'Password is required'}
    )

    @pre_load
    def normalize_email(self, data, **kwargs):
        if 'email' in data and isinstance(data['email'], str):
            data['email'] = data['email'].lower().strip()
        return data


class UserUpdateSchema(Schema):
    """
    Nota: el email y el password NO están aquí.
    Cambiar email y cambiar contraseña son operaciones
    separadas con sus propios endpoints y validaciones específicas
    (ej: cambio de contraseña requiere la contraseña actual).
    """

    first_name = fields.Str(validate=validate.Length(min=1, max=100))
    last_name  = fields.Str(validate=validate.Length(min=1, max=100))
    phone      = fields.Str(allow_none=True, validate=validate.Length(max=20))

    @validates('first_name')
    def validate_first_name(self, value):
        if not value.strip():
            raise ValidationError('The name cannot be just spaces.')

    @validates('last_name')
    def validate_last_name(self, value):
        if not value.strip():
            raise ValidationError('The surname cannot be just spaces.')


class UserChangePasswordSchema(Schema):

    current_password = fields.Str(
        required=True,
        load_only=True,
        error_messages={'required': 'Your current password is required'}
    )
    new_password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8, error='The new password must be at least 8 characters long')
    )
    new_password_confirm = fields.Str(required=True, load_only=True)

    @validates('new_password')
    def validate_password_strength(self, value):
        if not any(char.isdigit() for char in value):
            raise ValidationError('The new password must contain at least one number')
        if not any(char.isalpha() for char in value):
            raise ValidationError('The new password must contain at least one letter')

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get('new_password') != data.get('new_password_confirm'):
            raise ValidationError(
                {'new_password_confirm': ['The passwords do not match']}
            )


class UserResponseSchema(Schema):
    """
    Puntos clave:
    - password_hash NUNCA aparece aquí
    - full_name es una propiedad calculada del modelo
    - dump_default: valor si el atributo es None al serializar
    - Los timestamps se formatean como ISO 8601 (estándar internacional)
    """

    id         = fields.Int()
    first_name = fields.Str()
    last_name  = fields.Str()
    full_name  = fields.Str()        # Propiedad @property del modelo
    email      = fields.Str()
    phone      = fields.Str(dump_default=None)
    role       = fields.Str()
    is_active  = fields.Bool()
    created_at = fields.DateTime(format='iso')
    updated_at = fields.DateTime(format='iso')



user_register_schema  = UserRegisterSchema()
user_login_schema     = UserLoginSchema()
user_update_schema    = UserUpdateSchema()
user_change_password_schema = UserChangePasswordSchema()
user_response_schema  = UserResponseSchema()
users_response_schema = UserResponseSchema(many=True)   # Para listas de usuarios