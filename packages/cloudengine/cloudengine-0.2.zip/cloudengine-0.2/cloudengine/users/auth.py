import re
from cloudengine.users.signals import (
                           app_user_login_failed, 
                           app_user_logged_in,
                           app_user_logged_out
                           )
from cloudengine.users.backends import ModelBackend
from cloudengine.users.middleware import SESSION_KEY

from django.middleware.csrf import rotate_token


def _clean_credentials(credentials):
    """
    Cleans a dictionary of credentials of potentially sensitive info before
    sending to less secure functions.

    Not comprehensive - intended for app_user_login_failed signal
    """
    SENSITIVE_CREDENTIALS = re.compile('api|token|key|secret|password|signature', re.I)
    CLEANSED_SUBSTITUTE = '********************'
    for key in credentials:
        if SENSITIVE_CREDENTIALS.search(key):
            credentials[key] = CLEANSED_SUBSTITUTE
    return credentials

        
def authenticate(**credentials):
    """
    If the given credentials are valid, return a AppUser object.
    """
    backend = ModelBackend()
    user = backend.authenticate(**credentials)
    if user:
        return user

    app_user_login_failed.send(sender=__name__,
            credentials=_clean_credentials(credentials))


def login(request, user):
    """
    Persist a user id in the request. This way a user doesn't
    have to reauthenticate on every request. Note that data set during
    the anonymous session is retained when the user logs in.
    """
    if user is None:
        user = request.app_user
    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != user.pk:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()
    request.session[SESSION_KEY] = user.pk
    if hasattr(request, 'app_user'):
        request.app_user = user
    rotate_token(request)
    app_user_logged_in.send(sender=user.__class__, request=request, user=user)


def logout(request):
    """
    Removes the authenticated user's ID from the request and flushes their
    session data.
    """
    # Dispatch the signal before the user is logged out so the receivers have a
    # chance to find out *who* logged out.
    user = getattr(request, 'app_user', None)
    if hasattr(user, 'is_authenticated') and not user.is_authenticated():
        user = None
    app_user_logged_out.send(sender=user.__class__, request=request, user=user)

    request.session.flush()
    if hasattr(request, 'app_user'):
        from cloudengine.users.models import AnonymousAppUser
        request.app_user = AnonymousAppUser()
