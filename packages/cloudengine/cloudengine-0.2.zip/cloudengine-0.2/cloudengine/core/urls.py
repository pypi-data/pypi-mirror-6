from django.conf.urls import patterns, url
from django.contrib import admin
from cloudengine.core.views import MyRegistrationView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'cloudengine.core.views.index', name='index'),
    url(r'^accounts/register/$', MyRegistrationView.as_view()),
    
)