# Create your views here.

from django.views.generic import TemplateView

        
class AppDataView(TemplateView):
    template_name= "app_data.html"
    
    