from __future__ import unicode_literals
import re
import warnings
import datetime
import hashlib
import random
from cloudengine.core.models import CloudApp

from cloudengine.users.signals import app_user_logged_in
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.core import validators
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
# UNUSABLE_PASSWORD is still imported here for backwards compatibility
from django.contrib.auth.hashers import (
    check_password, make_password, is_password_usable)

from django.utils.encoding import python_2_unicode_compatible
from django.template.loader import render_to_string
from django.conf import settings
try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now
    
SHA1_RE = re.compile('^[a-f0-9]{40}$')

def update_last_login(sender, user, **kwargs):
    """
    A signal receiver which updates the last_login date for
    the user logging in.
    """
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
app_user_logged_in.connect(update_last_login)


class SiteProfileNotAvailable(Exception):
    pass


class BaseAppUserManager(models.Manager):

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the address by lowercasing the domain part of the email
        address.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])
        return email

    def make_random_password(self, length=10,
                             allowed_chars='abcdefghjkmnpqrstuvwxyz'
                                           'ABCDEFGHJKLMNPQRSTUVWXYZ'
                                           '23456789'):
        """
        Generates a random password with the given length and given
        allowed_chars. Note that the default value of allowed_chars does not
        have "I" or "O" or letters and digits that look similar -- just to
        avoid confusion.
        """
        return get_random_string(length, allowed_chars)

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})


class AppUserManager(BaseAppUserManager):

    def create_user(self, username, password, site,
                    email=None, verify_email=True, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = AppUserManager.normalize_email(email)
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        if isinstance(username, unicode):
            encoded = username.encode('utf-8')
        activation_key = hashlib.sha1(salt+encoded).hexdigest()
        user = self.model(username=username, email=email,
                          activation_key=activation_key,
                          email_verified=False,                          is_active=True, last_login=now,
                          date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        if verify_email and email:
            user.send_activation_email(site)
        
        return user
    
    def verify_password_reset_key(self, app_name, password_reset_key):
        if SHA1_RE.search(password_reset_key):
            print "valid sha key" + password_reset_key
            try:
                user = self.get(app__name = app_name, password_reset_key=password_reset_key)
            except self.model.DoesNotExist:
                return False
            #user.password_reset_key = "None"
            #user.save()
            return user
        return False
    
    def confirm_email_verify(self, app_name, activation_key):
        """
        Validate an activation key and activate the corresponding
        ``User`` if valid.
        
        If the key is valid and has not expired, return the ``User``
        after activating.
        
        If the key is not valid or has expired, return ``False``.
        
        If the key is valid but the ``User`` is already active,
        return ``False``.
        
        To prevent reactivation of an account which has been
        deactivated by site administrators, the activation key is
        reset to the string constant ``ACTIVATED``
        after successful activation.

        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                user = self.get(app__name = app_name, activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not user.activation_key_expired():
                user.email_verified = True
                user.activation_key = self.model.ACTIVATED
                user.save()
                return user
        return False


@python_2_unicode_compatible
class AbstractBaseAppUser(models.Model):
    password = models.CharField(_('password'), max_length=128)
    last_login = models.DateTimeField(_('last login'), default=timezone.now)

    is_active = True

    REQUIRED_FIELDS = []

    class Meta:
        abstract = True

    def get_username(self):
        "Return the identifying username for this User"
        return getattr(self, self.USERNAME_FIELD)

    def __str__(self):
        return self.get_username()

    def natural_key(self):
        return (self.get_username(),)

    def is_anonymous(self):
        """
        Always returns False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = make_password(None)

    def has_usable_password(self):
        return is_password_usable(self.password)

    def get_full_name(self):
        raise NotImplementedError()

    def get_short_name(self):
        raise NotImplementedError()


class AbstractAppUser(AbstractBaseAppUser):
    """
    An abstract base class implementing a fully featured AppUser model.

    Username, password and email are required. Other fields are optional.
    """
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
        ])
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    activation_key = models.CharField(_('activation key'), max_length=40, blank=True)
    password_reset_key = models.CharField(_('password reset key'), max_length=40, blank=True)
    email_verified = models.BooleanField(_('verified email id'),default=False)

    objects = AppUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('App user')
        verbose_name_plural = _('App users')
        abstract = True

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        warnings.warn("The use of AUTH_PROFILE_MODULE to define user profiles has been deprecated.",
            PendingDeprecationWarning)
        if not hasattr(self, '_profile_cache'):
            from django.conf import settings
            if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
                raise SiteProfileNotAvailable(
                    'You need to set AUTH_PROFILE_MODULE in your project '
                    'settings')
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            except ValueError:
                raise SiteProfileNotAvailable(
                    'app_label and model_name should be separated by a dot in '
                    'the AUTH_PROFILE_MODULE setting')
            try:
                model = models.get_model(app_label, model_name)
                if model is None:
                    raise SiteProfileNotAvailable(
                        'Unable to load the profile model, check '
                        'AUTH_PROFILE_MODULE in your project settings')
                self._profile_cache = model._default_manager.using(
                                   self._state.db).get(user__id__exact=self.id)
                self._profile_cache.user = self
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return self._profile_cache


class AppUser(AbstractAppUser):
    """
    App Users within the CloudEngine authentication system are represented by this
    model.

    Username, password and email are required. Other fields are optional.
    """
    ACTIVATED = u"ALREADY_ACTIVATED"
    
    app = models.ForeignKey(CloudApp)
    
    
    def __unicode__(self):
        return unicode(self.username)
    
    def activation_key_expired(self):
        """
        Determine whether this ``User``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.
        
        Key expiration is determined by a two-step process:
        
        1. If the user has already activated, the key will have been
           reset to the string constant ``ACTIVATED``. Re-activating
           is not permitted, and so this method returns ``True`` in
           this case.

        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``EMAIL_VERIFICATION_DAYS`` (which should be the number of
           days after sending the verification email during which user
           is allowed to verify his email); if the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.
        
        """
        expiration_date = datetime.timedelta(days=settings.EMAIL_VERIFICATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
               (self.date_joined + expiration_date <= datetime_now())
    activation_key_expired.boolean = True

    def send_activation_email(self, site):
        
        ctx_dict = {'app' : self.app,
                    'activation_key': self.activation_key,
                    'expiration_days': settings.EMAIL_VERIFICATION_DAYS,
                    'site': site
                    }
        subject = render_to_string('activation_email_subject.txt',
                                   ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        
        message = render_to_string('activation_email.txt',
                                   ctx_dict)
        
        self.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
        
    def send_password_reset_email(self, site):
        
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        if isinstance(self.username, unicode):
            encoded = self.username.encode('utf-8')
        password_reset_key = hashlib.sha1(salt+encoded).hexdigest()
        
        self.password_reset_key  = password_reset_key
        self.save()
        
        ctx_dict = {'app' : self.app,
                    'password_reset_key': self.password_reset_key,
                    'site': site
                    }
        subject = render_to_string('password_reset_email_subject.txt',
                                   ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        
        message = render_to_string('password_reset_email.txt',
                                   ctx_dict)
        
        self.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)


@python_2_unicode_compatible
class AnonymousAppUser(object):
    id = None
    pk = None
    username = ''
    is_active = False

    def __init__(self):
        pass

    def __str__(self):
        return 'AnonymousAppUser'

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1  # instances always return the same hash value

    def save(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def set_password(self, raw_password):
        raise NotImplementedError

    def check_password(self, raw_password):
        raise NotImplementedError

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False
