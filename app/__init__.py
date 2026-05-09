from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config.settings import config_map

# Instancias de extensiones 
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app (config_name: str = 'default') -> Flask:

    app = Flask(__name__)

    # Cargar configuración según el ambiente
    app.config.from_object(config_map.get(config_name, config_map['default']))

    # Inicializar extensiones
    db.init_app(app)         
    migrate.init_app(app, db)  
    jwt.init_app(app) 

    # CORS: permite que un frontend (ej: React en localhost:3000)
    # pueda hacer requests a nuestra API
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Un Blueprint es un grupo de rutas relacionadas.
    # Los importamos aquí para evitar importaciones circulares.
    from app.routes.api_v1 import api_v1_blueprint
    app.register_blueprint(api_v1_blueprint, url_prefix='/api/v1')

    #egistrar manejadores de errores globales
    _register_error_handlers(app)
    
    return app

def _register_error_handlers(app: Flask) -> None:
    """
    Registra manejadores de errores HTTP globales.
    Cuando Flask encuentra estos errores, usa estas funciones
    para devolver respuestas JSON consistentes.
    """

    from app.utils.response_helper import error_response
    
    @app.errorhandler(404)
    def not_found(error):
        return error_response("Resource not found", 404)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response("HTTP method not allowed", 405)
    
    @app.errorhandler(500)
    def internal_error(error):
        # En producción NO exponemos detalles del error interno
        return error_response("Internal Server Error", 500)




"""
Application Factory de Flask.

¿Qué es el patrón Application Factory?
En vez de crear la app Flask como una variable global,
la creamos dentro de una función. Esto nos permite:
1. Crear múltiples instancias con distintas configs (útil para tests)
2. Evitar importaciones circulares
3. Inicializar extensiones de forma limpia y ordenada

Es el patrón recomendado por la documentación oficial de Flask.
"""