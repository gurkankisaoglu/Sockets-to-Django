from django import forms

from img_tool_app.models import Image


class loadImageForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ("img",)
