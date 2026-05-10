

import logging
import time
from flask import request, g

# Configurar el logger para este módulo
# El nombre 'cinema_api' aparecerá en cada línea de log
logger = logging.getLogger('cinema_api')


def register_logging_middleware(app):

    # Configurar formato de logs si estamos en desarrollo
    if app.config.get('DEBUG'):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # En producción: solo WARNING y superior, formato más compacto
        logging.basicConfig(
            level=logging.WARNING,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )

    @app.before_request
    def log_request_start():

        # time.time() devuelve segundos desde epoch (flotante)
        g.request_start_time = time.time()

        # Log de debug: cada request entrante
        # En producción podrías omitir esto o guardarlo en un archivo separado
        logger.debug(
            'REQUEST  %s %s | IP: %s | User-Agent: %s',
            request.method,
            request.path,
            request.remote_addr,
            request.headers.get('User-Agent', 'Unknown')[:50]  # Truncar para no saturar los logs
        )

    @app.after_request
    def log_request_end(response):

        # Calcular duración del request
        duration_ms = None
        if hasattr(g, 'request_start_time'):
            duration_ms = round((time.time() - g.request_start_time) * 1000, 2)

        # Determinar nivel de log según el status code
        status_code = response.status_code

        if status_code >= 500:
            # Errores del servidor — críticos
            log_func = logger.error
        elif status_code >= 400:
            # Errores del cliente — warnings
            log_func = logger.warning
        else:
            # Respuestas exitosas — debug
            log_func = logger.debug

        # El user_id viene de g si el middleware de auth ya lo cargó
        user_id = getattr(g, 'current_user_id', None)

        log_func(
            'RESPONSE %s %s | Status: %s | Duration: %sms | User: %s',
            request.method,
            request.path,
            status_code,
            duration_ms,
            user_id or 'anonymous'
        )

        # IMPORTANTE: siempre devolver la respuesta
        return response

    @app.teardown_request
    def log_errors(exception):
    
        if exception:
            logger.error(
                'UNHANDLED EXCEPTION in %s %s: %s',
                request.method,
                request.path,
                str(exception),
                exc_info=True  # Incluye el stack trace completo
            )


"""
Middleware de logging.

Registra información de cada request y response.
Esencial en producción para:
- Debuggear problemas reportados por usuarios
- Monitorear el rendimiento de la API
- Detectar patrones de uso inusuales (posibles ataques)
- Auditoría de operaciones

Usamos el módulo logging estándar de Python.
En producción conectarías esto a un servicio como:
- CloudWatch (AWS)
- Stackdriver (Google Cloud)
- Papertrail
- Datadog
"""