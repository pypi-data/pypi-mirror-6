from django.conf.urls import patterns, url
from cloudengine.files.views import AppFilesView
#

# todo: rest api -- allow traversing api through urls??

urlpatterns = patterns('',
                       # Examples:
                       #url(r'^$', FileList.as_view(), name="files-app-home"),
                       # todo: the regex decides the allowed filenames.
                       # standardize filenames
                       # todo: add testcases for all possible filenames
                       url(r'^$', AppFilesView.as_view(),
                          name="cloudengine-app-files"),
                       url(r'^upload/$', AppFilesView.as_view()),
                        

                       )

