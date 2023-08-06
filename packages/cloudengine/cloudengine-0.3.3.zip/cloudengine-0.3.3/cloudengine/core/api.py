from rest_framework.views import APIView
from rest_framework.response import Response
from cloudengine.core.models import CloudApp


# View for creating new apps
class AppView(APIView):

    def post(self, request, name):
        app = CloudApp(name=name)
        app.save()
        return Response({"id": app.key})


class AppListView(APIView):

    def get(self, request):
        app_props = ['name', 'key']
        app_list = []
        apps = CloudApp.objects.all()
        for app in apps:
            new_app = {}
            for prop in app_props:
                new_app[prop] = getattr(app, prop)
            app_list.append(new_app)
        return Response({'result': app_list})
