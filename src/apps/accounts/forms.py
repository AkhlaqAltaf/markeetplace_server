from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from src.apps.accounts.models import CustomUser

class CustomLoginForm(forms.Form):
    email = forms.EmailField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise forms.ValidationError(_("Invalid credentials."))
        if not user.is_verified:
            raise forms.ValidationError(_("Email is not verified. Please verify your email first."))

        cleaned_data['user'] = user
        return cleaned_data


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = CustomUser
        fields = ['email', 'password']  # Only email and password for registration

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data