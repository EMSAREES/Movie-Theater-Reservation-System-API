from flask import request, g
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity,
    exceptions as jwt_exceptions
)
from functools import wraps


def register_auth_middleware(app):
    """
    @app.before_request: la función se llama ANTES de cada request.
    Si devuelve algo (una Response), Flask la usa directamente
    y NO llama al controlador. Si devuelve None, Flask continúa.
    """

    @app.before_request
    def load_current_user():
        """
        Intenta cargar el usuario actual en g.current_user.

        g es el contexto global de Flask para el request actual.
        Es como una mochila que vive durante un request y luego desaparece.
        Perfecta para pasar datos entre middlewares y controladores.

        Esta función NO falla si no hay token (las rutas públicas
        no tienen token y eso está bien). Solo carga el usuario
        si el token existe y es válido.
        """

        # Inicializamos siempre en None
        g.current_user = None
        g.current_user_id = None

        # Intentar verificar el JWT sin lanzar error si no existe
        try:
            # verify_jwt_in_request(optional=True):
            # - Si hay token válido: lo verifica y lo carga
            # - Si no hay token: no hace nada (no lanza error)
            # - Si el token es inválido/expirado: sí lanza error
            verify_jwt_in_request(optional=True)

            user_id_str = get_jwt_identity()

            if user_id_str:
                g.current_user_id = int(user_id_str)

                # Cargar el usuario desde la BD
                # Esto hace UNA query por request para rutas autenticadas
                from app.models.user import User
                user = User.query.get(g.current_user_id)

                if user and user.is_active:
                    g.current_user = user
                elif user and not user.is_active:
                    # El token es válido pero el usuario fue desactivado
                    # Devolvemos 401 para que el cliente refresque/limpie su token
                    from app.utils.response_helper import error_response
                    return error_response(
                        'Tu cuenta ha sido desactivada. Contacta al administrador.',
                        401
                    )

        except jwt_exceptions.NoAuthorizationError:
            # No hay header Authorization — es normal en rutas públicas
            pass
        except jwt_exceptions.InvalidHeaderError:
            # Header Authorization mal formado
            # Lo ignoramos aquí; @jwt_required() lo capturará si la ruta lo requiere
            pass
        except Exception:
            # Cualquier otro error de JWT lo ignoramos en el middleware
            # El decorador @jwt_required() en las rutas protegidas
            # lanzará el error apropiado
            pass


def admin_required(f):
    """
    Decorador para rutas que requieren rol de administrador.

    Uso:
        @app.route('/admin/users')
        @jwt_required()
        @admin_required
        def list_all_users():
            ...

    Debe usarse DESPUÉS de @jwt_required() porque necesita
    que el JWT ya haya sido verificado y g.current_user cargado.

    ¿Por qué un decorador y no un middleware global?
    Porque solo algunas rutas son de admin. Un middleware global
    que verifica rol en TODAS las rutas protegidas sería
    demasiado restrictivo.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.utils.response_helper import error_response

        # Verificar que hay usuario autenticado
        if not g.current_user:
            return error_response('Authentication required', 401)

        # Verificar rol de administrador
        if g.current_user.role != 'admin':
            return error_response(
                'This action requires administrator permissions',
                403
            )

        return f(*args, **kwargs)

    return decorated_function


def same_user_or_admin(f):
    """
    Decorador para rutas donde el usuario puede acceder
    a sus propios recursos, o un admin puede acceder a cualquiera.

    Caso de uso: GET /api/v1/users/<user_id>
    - El usuario puede ver su propio perfil
    - Un admin puede ver cualquier perfil
    - Un usuario NO puede ver el perfil de otro usuario

    Asume que la ruta tiene un parámetro <int:user_id>.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.utils.response_helper import error_response

        if not g.current_user:
            return error_response('Authentication required', 401)

        # Obtener el user_id del parámetro de la URL
        target_user_id = kwargs.get('user_id')

        is_own_resource = (g.current_user.id == target_user_id)
        is_admin = (g.current_user.role == 'admin')

        if not is_own_resource and not is_admin:
            return error_response(
                'You do not have permission to access this resource',
                403
            )

        return f(*args, **kwargs)

    return decorated_function


def get_current_user():
    """
    Helper para obtener el usuario actual desde cualquier controlador.

    Uso en controladores:
        from app.middlewares.auth_middleware import get_current_user

        def my_endpoint():
            user = get_current_user()
            if user:
                return f"Hola {user.full_name}"

    Returns:
        El objeto User actual o None si no hay sesión.
    """
    return getattr(g, 'current_user', None)


def get_current_user_id():
    """
    Helper para obtener el ID del usuario actual.
    Más eficiente que get_current_user() cuando solo necesitas el ID.

    Returns:
        int con el user_id o None
    """
    return getattr(g, 'current_user_id', None)

"""
Middleware de autenticación.

¿Por qué un middleware de auth además de @jwt_required()?
@jwt_required() protege rutas individuales una por una.
El middleware aquí hace cosas ADICIONALES que aplican a
múltiples rutas de forma transversal:

1. Inyectar el usuario actual en g (Flask global context)
   para que cualquier controlador pueda acceder sin repetir código.

2. Registrar el user_id en los logs de cada request.

3. Verificar si el usuario está activo (un usuario puede tener
   un token válido pero su cuenta fue desactivada después).

4. Bloquear rutas de admin si el usuario no tiene el rol correcto.

Nota importante: Este middleware NO reemplaza @jwt_required().
@jwt_required() verifica que el token JWT sea válido y no haya expirado.
Este middleware hace verificaciones ADICIONALES después de eso.
"""