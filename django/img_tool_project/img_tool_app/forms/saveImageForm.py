from django import forms

from img_tool_app.models import Group


class saveImageForm(forms.Form):
    imageName = forms.CharField()
