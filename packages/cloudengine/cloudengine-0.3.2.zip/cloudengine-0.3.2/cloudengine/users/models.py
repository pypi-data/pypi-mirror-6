
from django.db import models
from django.contrib.auth.models import User, UserManager
from cloudengine.core.models import CloudApp




class AppUser(models.Model):
    user = models.ForeignKey(User, primary_key = True)
    app = models.ForeignKey(CloudApp)





    