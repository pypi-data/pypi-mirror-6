from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from api import UserClassView ,CurrentUserView, UserDetailView
from api import LoginView, LogoutView


# todo: this regex puts limit on the names that classes and objects can have
urlpatterns = patterns(
    '',
    url(r'^$', UserClassView.as_view()),
    url(r'^(?P<id>[0-9]+)/$', UserDetailView.as_view()),
    url(r'login/$', LoginView.as_view()),
    url(r'logout/$', LogoutView.as_view()),
    url(r'me/$', CurrentUserView.as_view()),


)   

urlpatterns = format_suffix_patterns(urlpatterns)
