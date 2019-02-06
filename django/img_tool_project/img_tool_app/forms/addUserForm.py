from django import forms

from img_tool_app.models import Group


class addUserForm(forms.Form):
    groupsDB = Group.objects.all()
    OPTIONS = (

    )
    for group in groupsDB:
        OPTIONS += ((group, group),)

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    groups = forms.TypedMultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple,
                                         choices=OPTIONS)
