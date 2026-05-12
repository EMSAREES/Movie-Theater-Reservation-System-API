
from typing import Any, Optional


class AppException(Exception):
    """
    Clase base de todas las excepciones de la aplicación.

    Todos los errores de dominio heredan de esta clase para que
    los controladores puedan capturarlos con un solo `except AppException`.
    """

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message     = message
        self.status_code = status_code

    def to_dict(self) -> dict:
        return {
            'message':     self.message,
            'status_code': self.status_code,
        }

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} [{self.status_code}]: {self.message}>'


# ── 404 Not Found ──────────────────────────────────────────────────────────────

class NotFoundException(AppException):
    """Recurso no encontrado en la base de datos."""

    def __init__(self, resource: str, identifier: Any = None):
        if identifier is not None:
            message = f"{resource} con id '{identifier}' no encontrado"
        else:
            message = f"{resource} no encontrado"
        super().__init__(message, status_code=404)


class MovieNotFoundException(NotFoundException):
    def __init__(self, movie_id: Optional[Any] = None):
        super().__init__("Película", movie_id)


class RoomNotFoundException(NotFoundException):
    def __init__(self, room_id: Optional[Any] = None):
        super().__init__("Sala", room_id)


class ScreeningNotFoundException(NotFoundException):
    def __init__(self, screening_id: Optional[Any] = None):
        super().__init__("Función", screening_id)


class TicketNotFoundException(NotFoundException):
    def __init__(self, ticket_id: Optional[Any] = None):
        super().__init__("Ticket", ticket_id)


class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: Optional[Any] = None):
        super().__init__("Usuario", user_id)


# ── 409 Conflict ───────────────────────────────────────────────────────────────

class ConflictException(AppException):
    """
    Conflicto con el estado actual del recurso.
    Ej.: intentar crear algo que ya existe.
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class SeatAlreadyTakenException(ConflictException):
    """El asiento ya fue reservado por otro usuario."""
    def __init__(self, seat_number: str):
        super().__init__(
            f"El asiento '{seat_number}' ya está ocupado para esta función"
        )


class EmailAlreadyExistsException(ConflictException):
    """El email ya está registrado en el sistema."""
    def __init__(self, email: str):
        super().__init__(f"El email '{email}' ya está registrado")


class RoomNameAlreadyExistsException(ConflictException):
    """Ya existe una sala con ese nombre."""
    def __init__(self, name: str):
        super().__init__(f"Ya existe una sala con el nombre '{name}'")


class MovieTitleAlreadyExistsException(ConflictException):
    """Ya existe una película con ese título."""
    def __init__(self, title: str):
        super().__init__(f"Ya existe una película con el título '{title}'")


# ── 422 Business Rules / Validation ───────────────────────────────────────────

class ValidationException(AppException):
    """
    Error de validación de datos de entrada.
    errors puede contener una lista de mensajes específicos por campo.
    """
    def __init__(self, message: str, errors: Optional[list] = None):
        super().__init__(message, status_code=422)
        self.errors = errors or []


class BusinessRuleException(AppException):
    """
    Violación de una regla de negocio.
    Ej.: intentar reservar en una función ya iniciada.
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class ScreeningFullException(BusinessRuleException):
    """La función no tiene asientos disponibles."""
    def __init__(self):
        super().__init__("La función está completamente llena, no hay asientos disponibles")


class ScreeningAlreadyStartedException(BusinessRuleException):
    """No se puede reservar para una función que ya comenzó."""
    def __init__(self):
        super().__init__(
            "No se puede reservar un ticket para una función que ya inició o finalizó"
        )


class TicketAlreadyCancelledException(BusinessRuleException):
    """El ticket ya estaba cancelado."""
    def __init__(self):
        super().__init__("Este ticket ya se encuentra cancelado")


class TicketCancellationNotAllowedException(BusinessRuleException):
    """No se puede cancelar el ticket en el estado actual."""
    def __init__(self, reason: str):
        super().__init__(f"No se puede cancelar el ticket: {reason}")


# ── 401 / 403 Auth ────────────────────────────────────────────────────────────

class UnauthorizedException(AppException):
    """El cliente no está autenticado."""
    def __init__(self, message: str = "Autenticación requerida"):
        super().__init__(message, status_code=401)


class ForbiddenException(AppException):
    """El cliente está autenticado pero no tiene permiso para esta acción."""
    def __init__(self, message: str = "No tienes permiso para realizar esta acción"):
        super().__init__(message, status_code=403)



"""
Excepciones personalizadas del dominio de la aplicación.

¿Por qué excepciones propias?
──────────────────────────────
Las excepciones estándar de Python (ValueError, Exception) son demasiado
genéricas. Las nuestras tienen:
  1. Significado de negocio claro: SeatAlreadyTakenException habla por sí sola.
  2. El código HTTP correcto embebido: el controlador no necesita saber qué
     código usar, simplemente hace `return error_response(e.message, e.status_code)`.
  3. Mensajes listos para mostrar al usuario.

Patrón de uso en los servicios:
  raise MovieNotFoundException(movie_id)  ← legible, explícito

Patrón de captura en los controladores:
  except AppException as e:
      return error_response(e.message, e.status_code)
"""
