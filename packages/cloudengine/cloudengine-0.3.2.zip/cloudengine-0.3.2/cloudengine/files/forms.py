from django import forms


attrs_dict = {'class': 'required'}


class FileUploadForm(forms.Form):
    file = forms.FileField()
    app = forms.CharField(widget=forms.TextInput(attrs=attrs_dict))
