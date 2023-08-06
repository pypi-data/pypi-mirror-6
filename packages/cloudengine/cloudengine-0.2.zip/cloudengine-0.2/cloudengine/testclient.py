from django.test.client import Client
from rest_framework.authtoken.models import Token

# Please ensure the following app id is created
# by your corresponding test fixtures before using this client class.
# Token is generated automatically on creation of testclient user
TEST_APP_ID = ''


class MyTestClient(Client):

    def get_auth_token(self):
        return Token.objects.get(user__username="testclient")

    def request(self, **request):
        token = self.get_auth_token()
        token_header = "Token " + token.key
        return super(
            MyTestClient, self).request(HTTP_AUTHORIZATION=token_header,
                                        HTTP_APPID=TEST_APP_ID,
                                        **request)
