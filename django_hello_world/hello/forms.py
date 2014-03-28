from django import forms
from .models import MyData


class ProfileForm(forms.ModelForm):
    email = forms.CharField(label="Email", required=True)
    skype = forms.CharField(label="Skype", required=False)
    JID = forms.CharField(label="Jabber", required=False)

    class Meta:
        model = MyData
