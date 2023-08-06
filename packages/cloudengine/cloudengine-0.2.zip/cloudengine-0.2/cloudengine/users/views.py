import logging
import json
import StringIO
from cloudengine.core.cloudapi_view import CloudAPIView
from cloudengine.core.models import AppSettings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.conf import settings
from django.shortcuts import render_to_response
from django.views.generic import View
from django.template.response import TemplateResponse
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import (Http404,
                         HttpResponse)
from django.http import HttpResponseRedirect
from cloudengine.users.auth import authenticate, login, logout
from cloudengine.users.models import AppUser, AnonymousAppUser
from cloudengine.users.serializers import AppUserSerializer
from cloudengine.users.forms import SetPasswordForm


class UserClassView(CloudAPIView):
    logger = logging.getLogger("cloudengine")
    
    def get(self, request):
        app = request.META['app']
        serializer = AppUserSerializer(AppUser.objects.filter(app=app), many=True)
        return Response({"result": serializer.data})
        
    def post(self, request):
        data = None
        try:
            stream = StringIO.StringIO(request.body)
            data = JSONParser().parse(stream)
            data["app"] =  request.META['app']
        except Exception as e:
            self.logger.error("Unable to decode object. Error: %s"%str(e))
            return Response({"detail": "Invalid object."},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True) 
        
        new_user = AppUser(**data)
        try:
            new_user.full_clean()
        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
        # todo: decide if we need to verify users's email address
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        
        data["site"] = site
        app = request.META["app"]
        try:
            app_settings = AppSettings.objects.get(app = app)
            data["verify_email"] =  app_settings.verify_emails
        except AppSettings.DoesNotExist:
            pass
        
        new_user = AppUser.objects.create_user(**data)
        new_user.save()
        # Login the user
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
        if not hasattr(request, "app_user"):
            return Response({"detail": "incorrect username/password"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        user = request.app_user
        if isinstance(user, AnonymousAppUser):
            return Response({"detail": "user not logged in"})
        
        serializer = AppUserSerializer(request.app_user)
        return Response({"result": serializer.data})


class UserDetailView(CloudAPIView):
    logger = logging.getLogger("cloudengine")
    
    def get(self, request, id):
        user = AppUser.objects.get(pk = id)
        serializer = AppUserSerializer(user)
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


def verify_email(request, app_name):
    if request.method == "GET":
        token = request.GET.get("token", "")
        if token and app_name:
            try:
                user = AppUser.objects.confirm_email_verify(app_name , token)
                if user:
                    ctx = {'app': user.app}
                    return render_to_response('appuser_email_verified.html', ctx)
                else:
                    raise Http404()         #todo: render proper error page
            except AppUser.DoesNotExist:
                pass
        raise Http404()
    else:
        return HttpResponse("This HTTP method is not supported")


class PasswordResetRequest(CloudAPIView):
    
    def post(self, request):
        app = request.META['app']
        try:
            obj = json.loads(request.body)
            email = obj["email"]
            user = AppUser.objects.get(app=app, email=email)
        except Exception:
            return Response({"detail": "Invalid email id"},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        # todo: decide if we need to verify users's email address
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        user.send_password_reset_email(site)
        return Response()
    
    
class PasswordResetView(View):
    
    password_form = SetPasswordForm
    template_name = 'password_reset.html'
    
    def get(self, request, app_name, form = None):
        token = request.GET.get("token", "")
        if token and app_name:
            try:
                user = AppUser.objects.verify_password_reset_key(app_name=app_name, 
                                                                 password_reset_key=token)
                if user:
                    if not form:
                        form = self.password_form(None)
                    ctx = {'app': user.app,
                           'form': form
                           }
                    return TemplateResponse(request, 
                                            self.template_name,
                                            ctx
                                            )
                else:
                    raise Http404()
            except AppUser.DoesNotExist:
                pass
        raise Http404()
    
    def post(self, request, app_name):
        token = request.GET.get("token", "")
        if token and app_name:
            try:
                user = AppUser.objects.verify_password_reset_key(app_name=app_name, 
                                                                 password_reset_key=token)
                if user:
                    form = self.password_form(user, request.POST)
                    if form.is_valid():
                        form.save()
                        return HttpResponseRedirect(reverse('users.views.password_reset_complete', args=(app_name,)))
                    else:
                        return self.get(request, app_name, form)
                        
            except AppUser.DoesNotExist:
                pass
        raise Http404()
            
    
    @method_decorator(sensitive_post_parameters('new_password1', 'new_password2'))
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(PasswordResetView, self).dispatch(*args, **kwargs)


def password_reset_complete(request, app_name):
    template_name='password_reset_complete.html',
    context = { 'app': app_name}
    return TemplateResponse(request, template_name, context)


    