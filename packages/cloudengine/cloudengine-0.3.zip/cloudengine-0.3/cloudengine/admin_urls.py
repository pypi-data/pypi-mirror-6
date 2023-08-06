from django.conf.urls import patterns, url, include
from cloudengine.core.views import (CreateAppView, 
                AdminHomeView, AppView, AppSettingsView)

urlpatterns = patterns('',

                        url(r'^$', AdminHomeView.as_view(), 
                            name="cloudengine-admin-home"),
                        
                        url(r'^create_app/$', CreateAppView.as_view()),
                        url(r'^apps/(?P<app_name>[a-zA-Z0-9_\-]+)/$', 
                            AppView.as_view(), name="cloudengine-app-view"),
                       
                       url(r'^apps/(?P<app_name>[a-zA-Z0-9_\-]+)/data/', 
                            include('cloudengine.classes.urls')),
                       
                       url(r'^apps/(?P<app_name>[a-zA-Z0-9_\-]+)/files/', 
                            include('cloudengine.files.urls')),
                       
                       url(r'^apps/(?P<app_name>[a-zA-Z0-9_\-]+)/push/$', 
                            include('cloudengine.push.urls')),
                       
                       url(r'^apps/(?P<app_name>[a-zA-Z0-9_\-]+)/users/$', 
                            include('cloudengine.users.urls')),
                       
                       url(r'^apps/(?P<app_name>[a-zA-Z0-9_\-]+)/settings/$', 
                            AppSettingsView.as_view(), name="cloudengine-app-settings"),
                       )
