
from rest_framework import serializers
from models import CloudFile


class CloudFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloudFile
        fields = ('name', 'size', 'url')