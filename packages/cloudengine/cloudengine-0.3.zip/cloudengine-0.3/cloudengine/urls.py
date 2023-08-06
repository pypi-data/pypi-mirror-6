from django.conf.urls import patterns, include, url
from cloudengine.core.views import AccountKeysView
from django.views.generic import TemplateView

urlpatterns = patterns(
    '',
    # Examples:
    
    url(r'^$', TemplateView.as_view(template_name="index.html")),
    url(r'^admin/', include('cloudengine.admin_urls')),
    url(r'^api-auth/', include(
        'rest_framework.urls', namespace='rest_framework')),

    url(r'^socket.io/', 'cloudengine.push.views.socketio_view'),
    url(r'^api/v1/', include('cloudengine.api_v1_urls')),
    url(r'^files/', include('cloudengine.files.urls')),
    url(r'^keys/$',
        AccountKeysView.as_view(), name='myaccount-keys'),
    url(r'^accounts/', include(
        'registration.backends.simple.urls')),

)
