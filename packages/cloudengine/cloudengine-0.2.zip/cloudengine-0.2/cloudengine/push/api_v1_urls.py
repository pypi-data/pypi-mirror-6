from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from cloudengine.push.views import PushAPIView, PushSubscribers

urlpatterns = patterns('',
                       url(
                           r'^$',
                           PushAPIView.as_view(),
                           name='push-api-view'
                       ),

                       url(
                           r'^subscribers/$',
                           PushSubscribers.as_view(),
                           name='push-subscribers'
                       ),
                       )


urlpatterns = format_suffix_patterns(urlpatterns)
