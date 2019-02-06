from django import forms

from img_tool_app.models import Group


class setDefaultForm(forms.Form):
    OPTIONS = (
        ("ALLOW","ALLOW"),
        ("DENY", "DENY"),
        ("BLUR", "BLUR")
    )

    defaultAction = forms.ChoiceField(choices=OPTIONS, widget=forms.RadioSelect())
