from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.movie_controller     import MovieController
from app.controllers.user_controller      import UserController
from app.controllers.screening_controller import ScreeningController
from app.controllers.room_controller      import RoomController
from app.controllers.ticket_controller    import TicketController

# Blueprint con prefijo /api/v1 (aplicado en app/__init__.py)
api_v1_blueprint = Blueprint('api_v1', __name__)

# Instancias de controladores
movie_ctrl    = MovieController()
user_ctrl     = UserController()
screening_ctrl= ScreeningController()
room_ctrl     = RoomController()
ticket_ctrl   = TicketController()


# ── HEALTH CHECK ──────────────────────────────────────────────────────────────

@api_v1_blueprint.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificación de estado. Usado por servicios de monitoreo."""
    from app.utils.response_helper import success_response
    return success_response(
        data={"status": "healthy", "version": "1.0.0"},
        message="API funcionando correctamente"
    )


# ── USERS ─────────────────────────────────────────────────────────────────────

@api_v1_blueprint.route('/users/register', methods=['POST'])
def register():
    """Registrar nuevo usuario. No requiere autenticación."""
    return user_ctrl.register()


@api_v1_blueprint.route('/users/login', methods=['POST'])
def login():
    """Iniciar sesión. Devuelve JWT token."""
    return user_ctrl.login()


# ── MOVIES ────────────────────────────────────────────────────────────────────

@api_v1_blueprint.route('/movies', methods=['GET'])
def get_movies():
    """Lista películas activas con paginación y filtros. Público."""
    return movie_ctrl.get_all()


@api_v1_blueprint.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Detalle de una película. Público."""
    return movie_ctrl.get_by_id(movie_id)


@api_v1_blueprint.route('/movies', methods=['POST'])
@jwt_required()
def create_movie():
    """Crea una nueva película. Requiere JWT."""
    return movie_ctrl.create()


@api_v1_blueprint.route('/movies/<int:movie_id>', methods=['PUT'])
@jwt_required()
def update_movie(movie_id):
    """Actualiza una película. Requiere JWT."""
    return movie_ctrl.update(movie_id)


@api_v1_blueprint.route('/movies/<int:movie_id>', methods=['DELETE'])
@jwt_required()
def delete_movie(movie_id):
    """Soft-delete de una película. Requiere JWT."""
    return movie_ctrl.delete(movie_id)


# ── ROOMS ─────────────────────────────────────────────────────────────────────

@api_v1_blueprint.route('/rooms', methods=['GET'])
def get_rooms():
    """Lista todas las salas activas. Público."""
    return room_ctrl.get_all()


@api_v1_blueprint.route('/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    """Detalle de una sala. Público."""
    return room_ctrl.get_by_id(room_id)


@api_v1_blueprint.route('/rooms', methods=['POST'])
@jwt_required()
def create_room():
    """Crea una nueva sala. Requiere JWT."""
    return room_ctrl.create()


@api_v1_blueprint.route('/rooms/<int:room_id>', methods=['PUT'])
@jwt_required()
def update_room(room_id):
    """Actualiza una sala. Requiere JWT."""
    return room_ctrl.update(room_id)


@api_v1_blueprint.route('/rooms/<int:room_id>', methods=['DELETE'])
@jwt_required()
def delete_room(room_id):
    """Desactiva (soft-delete) una sala. Requiere JWT."""
    return room_ctrl.delete(room_id)


# ── SCREENINGS ────────────────────────────────────────────────────────────────

@api_v1_blueprint.route('/screenings', methods=['GET'])
def get_screenings():
    """Lista funciones programadas. Filtros: ?movie_id=X  ?date=YYYY-MM-DD"""
    return screening_ctrl.get_all()


@api_v1_blueprint.route('/screenings/<int:screening_id>', methods=['GET'])
def get_screening(screening_id):
    """Detalle de una función con película y sala."""
    return screening_ctrl.get_by_id(screening_id)


@api_v1_blueprint.route('/screenings/<int:screening_id>/seats', methods=['GET'])
def get_seats(screening_id):
    """Mapa de asientos disponibles/ocupados de una función."""
    return ticket_ctrl.get_seats_map(screening_id)


@api_v1_blueprint.route('/screenings', methods=['POST'])
@jwt_required()
def create_screening():
    """Crea una función. Requiere JWT."""
    return screening_ctrl.create()


@api_v1_blueprint.route('/screenings/<int:screening_id>', methods=['PUT'])
@jwt_required()
def update_screening(screening_id):
    """Actualiza precio/idioma/formato de una función. Requiere JWT."""
    return screening_ctrl.update(screening_id)


@api_v1_blueprint.route('/screenings/<int:screening_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_screening(screening_id):
    """Cancela una función programada. Requiere JWT."""
    return screening_ctrl.cancel(screening_id)


# ── TICKETS ───────────────────────────────────────────────────────────────────

@api_v1_blueprint.route('/tickets', methods=['GET'])
@jwt_required()
def get_my_tickets():
    """Lista los tickets del usuario autenticado."""
    return ticket_ctrl.get_my_tickets()


@api_v1_blueprint.route('/tickets/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    """Detalle de un ticket. Solo el dueño puede verlo."""
    return ticket_ctrl.get_by_id(ticket_id)


@api_v1_blueprint.route('/tickets', methods=['POST'])
@jwt_required()
def purchase_ticket():
    """Compra un ticket para una función. Requiere JWT."""
    return ticket_ctrl.purchase()


@api_v1_blueprint.route('/tickets/<int:ticket_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_ticket(ticket_id):
    """Cancela un ticket. Solo el dueño puede cancelarlo."""
    return ticket_ctrl.cancel(ticket_id)
