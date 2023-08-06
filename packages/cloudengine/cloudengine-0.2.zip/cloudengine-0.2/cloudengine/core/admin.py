from django.contrib import admin
from models import CloudApp 

class CloudAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'key')
    fields = ('name',)
    


admin.site.register(CloudApp, CloudAppAdmin)