from django.db import models
from cloudengine.core.models import CloudApp
from django.conf import settings


class CloudFile(models.Model):
    name = models.CharField(max_length=200)
    content = models.FileField(upload_to=settings.REMOTE_FILES_DIR)
    url = models.CharField(max_length=2000)
    size = models.BigIntegerField()
    app = models.ForeignKey(CloudApp)
