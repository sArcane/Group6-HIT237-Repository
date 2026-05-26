import logging


logger = logging.getLogger(__name__)


class AuthorizationAuditMiddleware:
    """Log authorization denials and enforce conservative browser policies."""

    protected_prefixes = ('/recordings/', '/analytics/', '/api/')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Set explicit browser policy headers to reduce data leakage paths.
        response.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')

        if request.path.startswith(self.protected_prefixes) and response.status_code in (401, 403):
            user_id = request.user.id if getattr(request, 'user', None) and request.user.is_authenticated else None
            logger.warning(
                'Authorization denied',
                extra={
                    'path': request.path,
                    'method': request.method,
                    'status_code': response.status_code,
                    'user_id': user_id,
                },
            )

        return response
