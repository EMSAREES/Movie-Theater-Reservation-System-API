import os
from app import create_app

config_name = os.environ.get('FLASK_ENV', 'development')

# Lee el ambiente desde la variable de entorno
# Si no existe, usa 'development' por defecto
config_name = os.environ.get('FLASK_ENV', 'development')

app = create_app(config_name)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',   # Acepta conexiones de cualquier IP
        port=5000,
        debug=app.config.get('DEBUG', False)
    )



"""
Punto de entrada de la aplicación.

Este archivo es el que ejecutamos para iniciar el servidor.
Es intencionalmente simple: solo crea la app y la ejecuta.
Toda la lógica de configuración está en app/__init__.py
"""
