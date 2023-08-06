from cloudengine.users.models import AppUser
from rest_framework import serializers


class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'email_verified')