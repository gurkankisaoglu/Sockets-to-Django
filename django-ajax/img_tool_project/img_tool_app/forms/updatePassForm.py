from django import forms


class updatePassForm(forms.Form):
    newPassword = forms.CharField(widget=forms.PasswordInput)
