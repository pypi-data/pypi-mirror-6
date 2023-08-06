from django.conf.urls import patterns, url
from cloudengine.classes.views import AppDataView



urlpatterns = patterns('',

                       url(r'^$', 
                            AppDataView.as_view(), name="cloudengine-app-data"),
                     
                       )
