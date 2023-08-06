from django.conf.urls import patterns, url
from cloudengine.users.views import AppUsersView
#


urlpatterns = patterns('',
                       # Examples:
                       url(r'^$', 
                            AppUsersView.as_view(), name="cloudengine-app-users"),
                      )

