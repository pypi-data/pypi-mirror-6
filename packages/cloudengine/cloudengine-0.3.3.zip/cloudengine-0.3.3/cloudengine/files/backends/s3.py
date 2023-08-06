import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from cloudengine.files.backends.base import BaseFileStorage
from cloudengine.files.models import CloudFile
from cloudengine.files.exceptions import (FileNotFound,
                                          FileExists)
from boto.s3.connection import S3Connection


class S3Storage(BaseFileStorage):
    '''Amazon S3 storage for app file uploads'''
    
    def upload(self, filename, content, app):
        
        new_file = CloudFile(name=filename, app=app)
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        key = new_file.get_upload_loc(filename)
        
        # Raise exception if a file with the filename already exists
        if default_storage.exists(key):
            raise FileExists()
        
        new_file.size = content.size
        new_file.content.save(filename, content)

        url = conn.generate_url(
            settings.AWS_URL_EXPIRY, "GET", bucket=settings.AWS_STORAGE_BUCKET_NAME, key=key)
        new_file.url = url
        new_file.save()
        return new_file
    
    
    def delete(self, filename, app):
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        try:
            fileobj = CloudFile.objects.get(name=filename, app=app)
        except CloudFile.DoesNotExist:
            raise FileNotFound()
            
        fileobj.content.delete()
        fileobj.delete()
    
    