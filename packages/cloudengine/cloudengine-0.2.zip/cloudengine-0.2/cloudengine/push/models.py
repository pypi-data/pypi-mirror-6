from django.db import models
from cloudengine.core.models import CloudApp
# Create your models here.


class PushNotification(models.Model):
    app = models.ForeignKey(CloudApp)
    send_time = models.DateTimeField(auto_now_add=True)
    num_subscribers = models.IntegerField()
