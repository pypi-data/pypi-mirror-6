import logging
from models import CloudFile
from exceptions import FileTooLarge
from manager import FilesManager
from cloudengine.files.forms import FileUploadForm
from cloudengine.core.models import CloudApp
from django.views.generic import TemplateView
from django.conf import settings

logger = logging.getLogger("cloudengine")


class AppFilesView(TemplateView):
    
    template_name= "app_files.html"
    form = FileUploadForm()
    msg = ''
    
    def __init__(self):
        try:
            backend = settings.CLOUDFILE_BACKEND
            backend = __import__(backend)
            self.manager = FilesManager(backend = backend)
        except Exception:
            self.manager = FilesManager()
            
    
    def get_context_data(self, app_name):
        app  = CloudApp.objects.get(name = app_name)
        files = CloudFile.objects.filter(app = app)
        storage = 0
        for file in files:
            storage += file.size
        return {'app_name': app_name, 'files': files,
                'form' : self.form, 'msg': self.msg,
                'storage': storage
                }

    def post(self, request, *args, **kwargs):
        # validate app name
        myfile = request.FILES.get("file", None)
        app = request.POST.get("app", "")
        appobj = self.is_validapp(app)
        error_msg = ""
        if not myfile:
            error_msg = "Please select a file to upload."
        elif not appobj:
            error_msg = "Please select an app before uploading file."
        

        if error_msg:
            self.msg = error_msg
            return self.get(request, *args, **kwargs)

        filename = self.clean_filename(myfile.name)
        try:
            self.manager.upload(filename, myfile, appobj)
            self.msg = "File uploaded successfully!"
        except FileTooLarge as e:
            self.msg = str(e)
        except Exception as ex:
            self.msg = "Error uploading file"
            logger.error(str(ex))
        return self.get(request, *args, **kwargs)

    def is_validapp(self, app):
        try:
            return CloudApp.objects.get(name=app)
        except CloudApp.DoesNotExist:
            return False

    def clean_filename(self, name):
        return name.replace(' ', '-')
