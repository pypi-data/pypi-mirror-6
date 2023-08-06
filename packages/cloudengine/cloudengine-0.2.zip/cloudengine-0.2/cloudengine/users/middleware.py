from cloudengine.users.backends import ModelBackend
from django.utils.functional import SimpleLazyObject


SESSION_KEY = '_auth_app_user_id'

def get_user(request):
    from cloudengine.users.models import AnonymousAppUser
    try:
        user_id = request.session[SESSION_KEY]
        backend = ModelBackend()
        user = backend.get_user(user_id) or AnonymousAppUser()
    except KeyError:
        user = AnonymousAppUser()
    if not hasattr(request, '_cached_app_user'):
        request._cached_app_user = user
    return request._cached_app_user


class AuthenticationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), "The CloudEngine app user authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        request.app_user = SimpleLazyObject(lambda: get_user(request))


