import django

__all__ = ['User', 'get_user_model']

# Django 1.5+ compatibility
if django.VERSION >= (1, 5):
    from django.conf import settings
    from django.contrib.auth import get_user_model
    User = settings.AUTH_USER_MODEL if hasattr(settings, 'AUTH_USER_MODEL') else 'auth.User'

else:
    from django.contrib.auth.models import User

    def get_user_model():
        return User
