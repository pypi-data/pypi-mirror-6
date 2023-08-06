import json
from socketio import socketio_manage
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from cloudengine.core.cloudapi_view import CloudAPIView
from cloudengine.push.push_service import get_subscriber_count
from cloudengine.push.push_service import push_to_channel
from cloudengine.push.models import PushNotification
from cloudengine.push.push_service import DefaultNamespace


def socketio_view(request):
    socketio_manage(
        request.environ, {'/default': DefaultNamespace}, request=request)
    return HttpResponse()


class PushSubscribers(CloudAPIView):

    def get(self, request):
        app = request.META['app']
        channel = app.name
        count = get_subscriber_count(channel)
        return Response({"result": count})


class PushAPIView(CloudAPIView):

    def post(self, request):
        app = request.META['app']
        user = request.user.username
        channel = app.name
        count = get_subscriber_count(channel)
        try:
            body = json.loads(request.body)
            message = body["message"]
        except Exception:
            # body is probably urlencoded
            try:
                message = request.POST['message']
            except Exception:
                return Response("Invalid request. Check request format",
                                status=status.HTTP_400_BAD_REQUEST)

        push_to_channel(channel, message)
        notification = PushNotification(app=app, num_subscribers=count)
        notification.save()
        return Response({"result": count})
