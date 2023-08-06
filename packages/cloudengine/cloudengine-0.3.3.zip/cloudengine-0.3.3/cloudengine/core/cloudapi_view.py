import datetime
from django.utils.timezone import utc
from rest_framework.views import APIView
from rest_framework import HTTP_HEADER_ENCODING
from cloudengine.core.models import CloudAPI, CloudApp
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated


# A wrapper around APIView to capture miscelleneous data
# such as number of api requests as well as validate
# app id of each request
class CloudAPIView(APIView):

    # super's initial does a lot of heavy lifting
    # we log an api request after validation from APIView

    def initial(self, request, *args, **kwargs):
        super(CloudAPIView, self).initial(request, *args, **kwargs)
        self.authenticate_api_id(request)
        self.log_request(request)

    def authenticate_api_id(self, request):
        token = self.get_app_header(request)
        if not token:
            raise NotAuthenticated("App ID not provided")
        try:
            app = CloudApp.objects.get(pk=token)
        except CloudApp.DoesNotExist:
            # invalid app id
            raise AuthenticationFailed('Invalid App ID.')
        request.META['app'] = app

    def get_app_header(self, request):
        auth = request.META.get('HTTP_APPID', b'')
        if isinstance(auth, str):
            # Work around django test client oddness
            auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth

    def log_request(self, request):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        api = CloudAPI(time=now, api=request.path)
        api.save()
