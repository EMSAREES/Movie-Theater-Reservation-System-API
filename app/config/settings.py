import os
from dotenv import load_dotenv

# Load the variables from the .env file into the system environment
load_dotenv()

class BaseConfig:
    """
    Configuración base compartida por todos los ambientes.
    Los valores vienen de variables de entorno para mayor seguridad.
    """
    
    # os.environ.get() lee la variable de entorno de forma segura
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    
    # Deshabilitar el seguimiento de modificaciones de SQLAlchemy
    # (consume memoria innecesaria, se recomienda desactivarlo)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Construcción de la URL de conexión a PostgreSQL
    # Formato: postgresql://usuario:password@host:puerto/nombre_bd
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    # Configuración JWT (tokens de autenticación)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-prod')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    
    # Paginación por defecto
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(BaseConfig):
    """
    Configuración para desarrollo local.
    Debug activado para ver errores detallados.
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Muestra las queries SQL en consola (útil para debug)


class TestingConfig(BaseConfig):
    """
    Configuración para pruebas automatizadas.
    """
    TESTING = True
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{BaseConfig.DB_USER}:{BaseConfig.DB_PASSWORD}"
        f"@{BaseConfig.DB_HOST}:{BaseConfig.DB_PORT}/{BaseConfig.DB_NAME}"
    )

    SQLALCHEMY_ECHO = False


class ProductionConfig(BaseConfig):
    """
    Configuración para producción.
    Debug desactivado por seguridad (no exponer stack traces).
    """
    DEBUG = False
    SQLALCHEMY_ECHO = False


# Diccionario para seleccionar la configuración por nombre
# Usaremos: app.config.from_object(config_map[FLASK_ENV])
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}





"""
Configuraciones de la aplicación por ambiente.

¿Qué significa esto?
La aplicación puede funcionar en diferentes "modos" según el lugar o situación en que se use:

- Development (desarrollo): pensado para los programadores. Aquí se activa el modo debug,
  que muestra mensajes de error detallados y se usa una base de datos local para hacer pruebas.

- Testing (pruebas): se utiliza una base de datos separada, exclusiva para ejecutar pruebas
  automáticas. Así nos aseguramos de que las pruebas no afecten los datos reales.

- Production (producción): es el modo real, el que usan los usuarios finales. Aquí el debug
  está desactivado y se aplican configuraciones seguras (contraseñas, tokens, conexiones
  protegidas).

¿Por qué es útil?
Porque con una sola variable de entorno podemos cambiar el comportamiento completo de la app.
Es como tener un interruptor que decide si la aplicación está en modo "prueba", "desarrollo"
o "producción", sin necesidad de modificar el código.
"""