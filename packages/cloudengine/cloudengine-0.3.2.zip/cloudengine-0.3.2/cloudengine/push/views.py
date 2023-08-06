from socketio import socketio_manage
from django.http import HttpResponse
from django.views.generic import TemplateView
from cloudengine.push.push_service import DefaultNamespace


def socketio_view(request):
    socketio_manage(
        request.environ, {'/default': DefaultNamespace}, request=request)
    return HttpResponse()


    
class AppPushView(TemplateView):
    template_name= "app_push.html"
