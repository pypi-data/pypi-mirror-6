from django.views.generic import TemplateView
from cloudengine.core.models import CloudApp
from cloudengine.users.models import AppUser
   
class AppUsersView(TemplateView):
    template_name= "app_users.html"
    
    def get_context_data(self, app_name):
        app = CloudApp.objects.get(name = app_name)
        users = AppUser.objects.filter(app = app)
        userlist = [user.user for user in users]
        return {'users' : userlist, 'app_name': app_name}
        