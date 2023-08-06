import os
from django.db import models
from django.conf import settings
from cloudengine.core.models import CloudApp

# Will change depending upon backend
def get_upload_loc(self, filename):
    return '/'.join([self.app.name, filename ])

class CloudFile(models.Model):
    name = models.CharField(max_length=200)
    content = models.FileField(upload_to = get_upload_loc)
    url = models.CharField(max_length=2000, blank=True)
    size = models.BigIntegerField()
    app = models.ForeignKey(CloudApp)
'''    
    def save(self, *args, **kwargs):
        path = get_upload_loc(self, self.name)
        loc = os.path.split(path)[0]
        if not os.path.exists(loc):
            raise Exception("Unable to save file to %s"%path)
        
        super(CloudFile, self).save(*args, **kwargs)
'''