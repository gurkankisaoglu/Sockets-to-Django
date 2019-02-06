from django import forms

from img_tool_app.models import User


class addGroupForm(forms.Form):
    usersDB = User.objects.all()
    OPTIONS = (

    )
    for user in usersDB:
        OPTIONS += ((user, user),)

    groupname = forms.CharField()
