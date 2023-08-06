from cloudengine.exceptions import CloudException
from django.conf import settings


class FileNotFound(CloudException):
    
    def __str__(self):
        return u"Specified file was not found on the server"


class FileTooLarge(CloudException):
    
    def __str__(self):
        return u"File exceeds max file size limit of %s bytes."%settings.MAX_FILE_SIZE



class FileExists(CloudException):
    
    def __str__(self):
        return u"A file with the given name already exists."



