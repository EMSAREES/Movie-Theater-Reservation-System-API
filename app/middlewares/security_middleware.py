
from flask import request


def register_security_middleware(app):
    """Registra el middleware de seguridad en la app Flask."""

    @app.after_request
    def add_security_headers(response):
        """
        Agrega headers de seguridad a cada respuesta.

        Explicación de cada header:

        X-Content-Type-Options: nosniff
            Evita que el navegador intente adivinar el tipo de contenido.
            Protege contra ataques de MIME sniffing.

        X-Frame-Options: DENY
            Evita que la API sea embebida en un iframe.
            Protege contra clickjacking.

        X-XSS-Protection: 1; mode=block
            Activa el filtro XSS del navegador (legacy, para IE/Edge antiguos).

        Strict-Transport-Security (HSTS)
            Fuerza HTTPS en requests futuros.
            Solo en producción porque rompe el desarrollo en HTTP local.

        Content-Security-Policy
            Define qué recursos puede cargar el cliente.
            Para una API JSON, bloqueamos todo porque no servimos HTML/JS/CSS.

        Referrer-Policy
            Controla qué información de referrer se envía.

        Cache-Control
            Evita que respuestas con datos sensibles se cacheen.
        """

        # Headers de seguridad universales (aplican en todos los ambientes)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # No revelar información del servidor
        # Por defecto Flask agrega "Werkzeug/x.x.x Python/x.x.x"
        response.headers['Server'] = 'Cinema-API'

        # Para endpoints que devuelven datos sensibles (autenticación, tickets),
        # desactivar el caché del navegador
        sensitive_paths = ['/api/v1/users/', '/api/v1/tickets/']
        is_sensitive = any(request.path.startswith(p) for p in sensitive_paths)

        if is_sensitive:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
            response.headers['Pragma'] = 'no-cache'

        # Headers adicionales solo en producción
        if not app.config.get('DEBUG'):
            # HSTS: forzar HTTPS por 1 año
            # No activar en desarrollo porque rompería el HTTP local
            response.headers['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains'
            )

            # Content Security Policy para API pura JSON
            # default-src 'none' bloquea todo; frame-ancestors 'none' previene iframes
            response.headers['Content-Security-Policy'] = (
                "default-src 'none'; frame-ancestors 'none'"
            )

        return response

    @app.after_request
    def validate_content_type(response):
        """
        Verifica que los endpoints de la API siempre devuelvan JSON.

        Una API REST debe responder siempre con Content-Type: application/json.
        Si algún controlador devuelve HTML por error (ej: un error de Flask
        sin manejar), esto nos ayuda a detectarlo.

        Solo aplica a rutas de la API, no a rutas de salud o estáticas.
        """
        if request.path.startswith('/api/') and response.status_code != 204:
            # 204 No Content no tiene cuerpo, así que no necesita Content-Type
            content_type = response.content_type

            if 'application/json' not in content_type:
                # Log de advertencia — esto no debería pasar
                import logging
                logging.getLogger('cinema_api').warning(
                    'Non-JSON response in API route: %s %s returned %s',
                    request.method,
                    request.path,
                    content_type
                )

        return response
    
"""
Middleware de seguridad.

Agrega headers de seguridad HTTP a todas las respuestas.
Estos headers protegen contra ataques comunes como:
- XSS (Cross-Site Scripting)
- Clickjacking
- MIME sniffing
- Información expuesta sobre el servidor

Son estándar en APIs profesionales y herramientas como
OWASP los recomiendan para cualquier API en producción.
"""