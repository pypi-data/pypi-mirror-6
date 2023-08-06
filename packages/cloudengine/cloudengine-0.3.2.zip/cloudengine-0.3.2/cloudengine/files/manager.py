
from exceptions import FileNotFound, FileTooLarge
from django.conf import settings
from cloudengine.files.backends.default import DefaultStorage


class FilesManager(object):
    
    def __init__(self, backend=DefaultStorage):
        self.backend = backend()
    
    def upload(self, filename, uploaded_file, appobj):
        
        if uploaded_file.size > settings.MAX_FILESIZE:
            raise FileTooLarge()
        cloudfile = self.backend.upload(filename, uploaded_file, appobj)
        return cloudfile
        
    def delete(self, filename, app):
        try:
            self.backend.delete(filename, app)
        except Exception:
            raise FileNotFound()
        
