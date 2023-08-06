from django import forms
from hunger.models import InvitationCode

class InviteRequestForm(forms.ModelForm):
    class Meta:
        model = InvitationCode
        fields = ['email']
        widgets = {"email": forms.TextInput({"placeholder": "Enter your email"}), }