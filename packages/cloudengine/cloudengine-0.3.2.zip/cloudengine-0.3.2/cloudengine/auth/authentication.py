from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.authentication import get_authorization_header
from cloudengine.auth.models import Token, APIUser

'''
The auth class is similar to django-rest-framework's token auth except that it doesn't make
the assumption about every user having a unique token i.e. it allows for multiple
users to have the same token which is very useful in certain scenarios such as building
API for mobile apps. Also since CloudEngine handles user management separately, the purpose of
the auth is only to authorize the caller to call an API. Hence, the token auth maps an 
authorized request to an AnonymousUser.
'''
class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    model = Token
    
    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(auth[1], request)

    def authenticate_credentials(self, key, request):
        try:
            # Check if this is a valid token
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')
        # Get the underlying HttpRequest object
        request = request._request
        user = getattr(request, 'user', None)
        if not user or not user.is_active:
            return (APIUser(), token)
        else:
            return (user, token)

    def authenticate_header(self, request):
        return 'Token'
