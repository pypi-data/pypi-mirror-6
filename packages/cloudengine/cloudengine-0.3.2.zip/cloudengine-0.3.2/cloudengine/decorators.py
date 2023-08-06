from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test


def admin_view(function=None, redirect_field_name=REDIRECT_FIELD_NAME, 
               login_url=settings.login_url):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
