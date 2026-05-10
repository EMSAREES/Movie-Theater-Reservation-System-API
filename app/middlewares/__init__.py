from app.middlewares.auth_middleware import register_auth_middleware
from app.middlewares.logging_middleware import register_logging_middleware
from app.middlewares.security_middleware import register_security_middleware

def register_middlewares(app):
    """
    Registra todos los middlewares en la aplicación Flask.

    Se llama desde create_app() en app/__init__.py.
    El orden importa: se ejecutan en el orden en que se registran.

    Args:
        app: La instancia de Flask
    """
    register_logging_middleware(app)    # Primero: loguear el request
    register_auth_middleware(app)       # Segundo: verificar identidad
    register_security_middleware(app)   # Tercero: agregar headers de seguridad


__all__ = ['register_middlewares']


"""
Middlewares de la aplicación.

¿Qué es un middleware?
Es una función que se ejecuta ANTES o DESPUÉS de cada request,
de forma automática, sin que el controlador tenga que llamarla.

Flask tiene dos tipos de hooks para esto:
- @app.before_request  → se ejecuta ANTES del controlador
- @app.after_request   → se ejecuta DESPUÉS del controlador

Casos de uso comunes:
- Verificar autenticación en rutas protegidas
- Registrar logs de cada request
- Agregar headers de seguridad a todas las respuestas
- Medir el tiempo de respuesta de la API

En este proyecto los middlewares son funciones que se registran
en la app, no clases. Flask trabaja mejor con el patrón funcional.
"""