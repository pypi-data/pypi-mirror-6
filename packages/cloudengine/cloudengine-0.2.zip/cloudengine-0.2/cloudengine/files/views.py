import logging
import uuid
from models import CloudFile
from cloudengine.files.forms import FileUploadForm
from django.core.files.base import ContentFile
from django.template import RequestContext
from django.views.generic import View
from django.shortcuts import render
from cloudengine.core.cloudapi_view import CloudAPIView
from cloudengine.core.models import CloudApp
from rest_framework.response import Response
from boto.s3.connection import S3Connection
from django.core.files.storage import default_storage
from django.conf import settings

logger = logging.getLogger("cloudengine")

MAX_FILESIZE = 2 * 1024 * 1024      # 2 MB

AWS_URL_EXPIRY = 3600 * 24 * 265 * \
    20         # won't expire for a very long time


class FileListView(CloudAPIView):

    def get(self, request):
        app = request.META.get('app', None)
        if not app:
            return Response({"detail": "Invalid app id provided"},
                            status=400)
        cloudapp = CloudApp.objects.get(name=app.name)
        result = []
        try:
            fileslist = CloudFile.objects.filter(app=cloudapp)
            for file in fileslist:
                result.append({"name": file.name,
                               "size": file.size,
                               "url": file.user_url,
                               })
        except CloudFile.DoesNotExist, e:
            pass
        return Response({"result": result})


# make sure filename in the newly generated url (before query string) does
# end with trailing slash
# S3 is hard coded now. Allow other storages to be plugged in
class FileView(CloudAPIView):

    def post(self, request, filename):
        content_length = request.META.get("CONTENT_LENGTH", 0)
        content_length = int(content_length)
        body = request.body
        if (content_length > MAX_FILESIZE) or (len(body) > MAX_FILESIZE):
            logger.error("File too large. content_length %d size %d" %
                         (content_length, len(body)))
            return Response({'detail': 'File size too large'}, status=400)

        app = request.META.get('app', None)
        if not app:
            # We should not have reached here anyway
            return Response({'detail': 'App id not provided'}, status=401)
        new_file = CloudFile(name=filename, app=app)

        # generate a friendly url and return to the user
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        while True:
            id = uuid.uuid4()
            new_filename = str(id) + '-' + \
                filename          # Try a new name if already exists
            key = '/'.join([settings.REMOTE_FILES_DIR, new_filename])
            # check if such a file exists
            if not default_storage.exists(key):
                break
        cont_file = ContentFile(body)
        new_file.size = cont_file.size
        new_file.content.save(new_filename, cont_file)

        url = conn.generate_url(
            AWS_URL_EXPIRY, "GET", bucket=settings.AWS_STORAGE_BUCKET_NAME, key=key)
        new_file.url = url
        new_file.save()

        return Response({"url": url}, status=201)
    
    def delete(self, request, filename):
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        app = request.META.get('app', None)
        if not app:
            # We should not have reached here anyway
            return Response({'detail': 'App id not provided'}, status=401)
        try:
            fileobj = CloudFile.objects.get(name=filename, app=app)
        except CloudFile.DoesNotExist:
            return Response({'detail': 'File does not exist'}, status=401)
        fileobj.content.delete()
        fileobj.delete()
        return Response()


# This view doesn't have any authentication.
# Please ensure authentication using django auth, etc.
class FileBrowserView(View):

    def get(self, request, *args, **kwargs):
        form = FileUploadForm()
        c = {"form": form, "files_list": CloudFile.objects.all()}
        return render(request, self.template_name, c,
                      context_instance=RequestContext(request))

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
        elif myfile.size > MAX_FILESIZE:
            error_msg = "File too big. Max. file limit is 2 MB"

        if error_msg:
            c = {"form": FileUploadForm(), "error": error_msg}
            return render(request,
                          self.template_name,
                          c,
                          context_instance=RequestContext(request))

        filename = self.clean_filename(myfile.name)
        new_file = CloudFile(name=filename, app=appobj)

        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        while True:
            id = uuid.uuid4()
            new_filename = str(id) + '-' + \
                filename          # Try a new name if already exists
            key = '/'.join([settings.REMOTE_FILES_DIR, new_filename])
            # check if such a file exists
            if not default_storage.exists(key):
                break
        new_file.size = myfile.size
        new_file.content.save(new_filename, myfile)

        url = conn.generate_url(
            AWS_URL_EXPIRY, "GET", bucket=settings.AWS_STORAGE_BUCKET_NAME, key=key)
        new_file.url = url
        new_file.save()
        c = {
            "form": FileUploadForm(), "success": "File uploaded successfully!"}
        return render(request,
                      self.template_name,
                      c,
                      context_instance=RequestContext(request))

    def is_validapp(self, app):
        try:
            return CloudApp.objects.get(name=app)
        except CloudApp.DoesNotExist:
            return False

    def clean_filename(self, name):
        return name.replace(' ', '-')
