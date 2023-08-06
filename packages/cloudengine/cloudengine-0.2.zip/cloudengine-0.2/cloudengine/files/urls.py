from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from cloudengine.files.views import FileBrowserView
#

# todo: rest api -- allow traversing api through urls??

urlpatterns = patterns('',
                       # Examples:
                       #url(r'^$', FileList.as_view(), name="files-app-home"),
                       # todo: the regex decides the allowed filenames.
                       # standardize filenames
                       # todo: add testcases for all possible filenames
                       url(r'^$', FileBrowserView.as_view(),
                           name='files-browser'),
                       url(r'^upload/$', FileBrowserView.as_view()),

                       )

urlpatterns = format_suffix_patterns(urlpatterns)
