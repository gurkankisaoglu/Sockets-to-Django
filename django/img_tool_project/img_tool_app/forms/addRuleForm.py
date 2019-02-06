from django import forms

from img_tool_app.models import Group


class addRuleForm(forms.Form):
    OPTIONSACTION = (
        ("ALLOW", "ALLOW"),
        ("DENY", "DENY"),
        ("BLUR", "BLUR")
    )

    OPTIONSSHAPE = {
        ("CIRCLE", "CIRCLE"),
        ("POLYLINE", "POLYLINE"),
        ("RECTANGLE", "RECTANGLE")
    }

    effects = forms.CharField(required=True)
    action = forms.ChoiceField(required=True, choices=OPTIONSACTION, widget=forms.RadioSelect())
    shape = forms.ChoiceField(required=True, choices=OPTIONSSHAPE, widget=forms.RadioSelect())
    coordinates = forms.CharField(required=True)
