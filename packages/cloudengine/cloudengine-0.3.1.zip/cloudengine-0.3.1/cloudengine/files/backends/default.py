from django.core.files.storage import default_storage
from cloudengine.files.models import CloudFile
from cloudengine.files.exceptions import FileExists

class DefaultStorage(object):
    """
    Default file storage which just saves files in specified folder 
    """
    
    def upload(self, name, fileobj, app):
        "Upload a file"
        # Raise exception if a file with the filename already exists
        if default_storage.exists(name):
            raise FileExists()
        
        cloudfile = CloudFile(name=name, content=fileobj, 
                              size=fileobj.size, app=app)
        cloudfile.save()
        return cloudfile
    
    def download(self, name):
        "Download a file"
        #return response- header X-SendFile headers
    