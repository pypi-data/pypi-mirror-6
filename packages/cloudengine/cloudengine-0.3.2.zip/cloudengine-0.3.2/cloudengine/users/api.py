import logging
import json
import StringIO
from cloudengine.core.cloudapi_view import CloudAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, AnonymousUser
from serializers import UserSerializer
from models import AppUser

class UserClassView(CloudAPIView):
    
    logger = logging.getLogger("cloudengine")
    
    def get(self, request, *args, **kwargs):
        app = request.META["app"]
        app_users = AppUser.objects.filter(app = app)
        users = [app_user.user for app_user in app_users]
        serializer = UserSerializer(users, many=True)
        return Response({"result": serializer.data})
        
    def post(self, request):
        try:
            #todo: update first_name, last_name and other attributes
            stream = StringIO.StringIO(request.body)
            data = JSONParser().parse(stream)
            username = data["username"]
            password = data["password"]
            
        except Exception as e:
            self.logger.error("Unable to decode object. Error: %s"%str(e))
            return Response({"detail": "Invalid object."},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        app =  request.META['app']
        #todo: validate username and password
        user = User.objects.create_user(username = username, password = password)
        new_user = AppUser(user = user, app = app)
        try:
            new_user.full_clean()
        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
        
        new_user.save()
        user = authenticate(username=data["username"], password=data["password"])
        login(request, user)
        request.session.save()
        return Response({settings.SESSION_COOKIE_NAME : request.session.session_key,
                          "id" : user.id
                        },
                        status=status.HTTP_201_CREATED)
        
    def delete(self, request):
        app = request.META['app']
        try:
            users = AppUser.objects.filter(app = app)
            users.delete()
        except Exception:
            pass
        return Response({"detail": "All users of this app are deleted"})



class LoginView(CloudAPIView):
    logger = logging.getLogger("cloudengine")
    
    def post(self, request):
        try:
            credentials = json.loads(request.body)
        except Exception, e:
            self.logger.error("Unable to decode object. Error: %s"%str(e))
            return Response({"detail": "Invalid object."},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        try:
            #make sure the user object has username and password
            username = credentials["username"]
            password = credentials["password"]
        except KeyError:
            self.logger.error("Error: %s"%str(e))
            return Response({"detail": "username/password field missing"},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session.save()
                return Response({settings.SESSION_COOKIE_NAME : request.session.session_key})
            else:
                return Response({"detail": "User account is inactive"},
                            status=status.HTTP_400_BAD_REQUEST,
                            )
        else:
            return Response({"detail": "incorrect username/password"},
                            status=status.HTTP_400_BAD_REQUEST)


class LogoutView(CloudAPIView):
    
    def get(self, request):
        logout(request)
        return Response({"detail": "User logged out successfully"})


class CurrentUserView(CloudAPIView):
    
    def get(self, request):
        user = request.user
        print user.username
        print type(user)
        if isinstance(user, AnonymousUser):
            return Response({"detail": "user not logged in"})
        
        serializer = UserSerializer(user)
        return Response({"result": serializer.data})


class UserDetailView(CloudAPIView):
    logger = logging.getLogger("cloudengine")
    
    def get(self, request, id):
        user = AppUser.objects.get(pk = id)
        serializer = UserSerializer(user)
        return Response({"result": serializer.data})
    
    def put(self, request, id):
        try:
            stream = StringIO.StringIO(request.body)
            data = JSONParser().parse(stream)
        except Exception as e:
            self.logger.error("Unable to decode object. Error: %s"%str(e))
            return Response({"detail": "Invalid object."},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        # If valid, update the user
        user = AppUser.objects.get(pk=id)
        for key in data.keys():
            setattr(user, key, data[key])
        user.save()
        return Response({"detail": "User data updated successfully"})
        

    def delete(self, request, id):
        try:
            user = AppUser.objects.get(pk = id)
        except AppUser.DoesNotExist:
            return Response({"detail": "Invalid user id"},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        user.delete()
        return Response({"detail": "User deleted successfully"})



