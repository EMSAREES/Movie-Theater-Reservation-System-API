# app/exceptions/__init__.py
"""Paquete de excepciones personalizadas del dominio."""

from app.exceptions.app_exceptions import (
    AppException,
    NotFoundException,
    MovieNotFoundException,
    RoomNotFoundException,
    ScreeningNotFoundException,
    TicketNotFoundException,
    UserNotFoundException,
    ConflictException,
    SeatAlreadyTakenException,
    EmailAlreadyExistsException,
    ValidationException,
    BusinessRuleException,
    ScreeningFullException,
    ScreeningAlreadyStartedException,
    UnauthorizedException,
    ForbiddenException,
)

__all__ = [
    'AppException',
    'NotFoundException',
    'MovieNotFoundException',
    'RoomNotFoundException',
    'ScreeningNotFoundException',
    'TicketNotFoundException',
    'UserNotFoundException',
    'ConflictException',
    'SeatAlreadyTakenException',
    'EmailAlreadyExistsException',
    'ValidationException',
    'BusinessRuleException',
    'ScreeningFullException',
    'ScreeningAlreadyStartedException',
    'UnauthorizedException',
    'ForbiddenException',
]