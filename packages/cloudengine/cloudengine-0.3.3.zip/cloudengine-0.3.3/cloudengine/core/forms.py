import re
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


def validate_app_name(name):
    if not re.match('^[a-zA-Z0-9\-_]+$', name):
        raise ValidationError("Invalid app name.")


class CreateAppForm(forms.Form):
    #todo: add validator
    app_name = forms.CharField(
                               widget=forms.TextInput(attrs={'class': 'required'}),
                               error_messages={'required': 
                                               _("Please provide an app name")},
                               validators=[validate_app_name])

