class ContentSecurityPolicyMiddleware:
    """
    Sets a Content-Security-Policy (CSP) header on all HTTP responses.
    Disallows inline scripts (requires script-src 'self').
    Allows Google Fonts and local assets.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 'Content-Security-Policy' not in response:
            csp_directives = [
                "default-src 'self'",
                "script-src 'self'",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com",
                "img-src 'self' data: blob:",
                "connect-src 'self'",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            ]
            response['Content-Security-Policy'] = "; ".join(csp_directives)
        return response
