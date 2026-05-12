from flask_jwt_extended import create_access_token

from app.repositories.user_repository import UserRepository
from app.exceptions.app_exceptions import (
    UserNotFoundException,
    EmailAlreadyExistsException,
    UnauthorizedException
)


class UserService:
    """
    Servicio de Usuarios.

    Responsabilidades:
      - Registrar nuevos usuarios (validar email único, hashear contraseña).
      - Autenticar usuarios y emitir JWT.

    NO contiene lógica de BD (eso es el repositorio).
    NO contiene lógica HTTP (eso es el controlador).
    """

    def __init__(self):
        self.repo = UserRepository()

    def register(self, data: dict):
        """
        Registra un nuevo usuario.
        Email único (case-insensitive), contraseña hasheada con bcrypt.
        """
        from app.models.user import User

        email = data['email'].lower().strip()

        if self.repo.exists_by_email(email):
            raise EmailAlreadyExistsException(email)

        user = User(
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            email=email,
        )
        user.set_password(data['password'])

        self.repo.save(user)
        self.repo.commit()

        return user

    def login(self, data: dict) -> dict:
        """
        Autentica al usuario y devuelve un JWT de acceso.
        Mensaje genérico para no revelar si el email existe (anti-enumeración).
        """
        email = data['email'].lower().strip()
        user  = self.repo.find_by_email(email)

        if not user or not user.check_password(data['password']):
            raise UnauthorizedException("Email o contraseña incorrectos")

        if not user.is_active:
            raise UnauthorizedException("Cuenta desactivada. Contacta al administrador.")

        access_token = create_access_token(identity=str(user.id))

        return {
            "access_token": access_token,
            "token_type":   "Bearer",
            "user":         user,
        }
