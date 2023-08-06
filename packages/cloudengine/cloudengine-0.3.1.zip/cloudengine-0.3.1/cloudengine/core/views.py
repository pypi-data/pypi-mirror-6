
from django.views.generic import TemplateView
from django.core.context_processors import csrf
from django.http import HttpResponse
from cloudengine.core.forms import CreateAppForm
from cloudengine.core.models import CloudApp
from cloudengine.auth.models import Token

class AccountKeysView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(AccountKeysView, self).get_context_data(**kwargs)
        apps = CloudApp.objects.all()
        context['apps'] = apps
        try:
            token = Token.objects.get(user=self.request.user)
            context['api_key'] = token.key
        except Token.DoesNotExist:
            context['api_key'] = ''
        return context


class AdminHomeView(TemplateView):
    template_name = 'admin_home.html'
    
    def get_context_data(self):
        apps = CloudApp.objects.all()
        return {'apps': apps}


class CreateAppView(TemplateView):
    template_name = "create_app.html"
    form = CreateAppForm()
    msg  = ""
    
    def get_context_data(self):
        context = {}
        context.update(csrf(self.request))
        context['form'] = self.form
        context["msg"] = self.msg
        return context
        
    def post(self, request):
        form = CreateAppForm(request.POST)
        if form.is_valid():
            app_name = form.cleaned_data['app_name']
            myapp = CloudApp(app_name)
            myapp.save()
            self.msg = "App created successfully!"
        else:
            self.form = form
        
        return self.get(request)
    
class AppView(TemplateView):
    template_name= "app.html"
    
    def get_context_data(self, app_name):
        return {"app_name" : app_name}
        
    def delete(self, request, app_name):
        print "app dlete called"
        return HttpResponse("app  delete method called")

    
class AppSettingsView(TemplateView):
    template_name= "app_settings.html"

    def get_context_data(self, app_name):
        app = CloudApp.objects.get(name=app_name)
        token = Token.objects.get()
        return { 'app_name': app_name, 'app': app,
                'token': token}

        