from .models import User

def current_user(request):
    """
    Context processor to add the current user to template context
    """
    user = None
    if request.user.is_authenticated:
        user = request.user
    return {
        'user': user
    }