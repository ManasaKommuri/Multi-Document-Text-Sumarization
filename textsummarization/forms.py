from django import forms
from django.forms import FileField

class DocumentForm(forms.Form):
    document =FileField()