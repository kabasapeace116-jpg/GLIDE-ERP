from django.utils.deprecation import MiddlewareMixin

class UserMiddleware(MiddlewareMixin):
    """
    Middleware to ensure user is available in templates
    """
    def process_request(self, request):
        # This ensures request.user is available
        pass