from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation

from src.apps.accounts.models import CustomUser
from django.contrib.auth import login , logout

class CustomLoginForm(forms.Form):
    email = forms.EmailField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        print("EMAIL..: ", email)
        print("PASSWORD..: ", password)
        
        # Check if email and password are valid (without the authenticate method)
        try:
            user = CustomUser.objects.get(email=email)
            print("USER ;;;...",user)

            print(user.check_password(password))
            if not user.check_password(password):  # Check if the password matches
                raise forms.ValidationError(_("Invalid credentials."))
        except CustomUser.DoesNotExist:
            raise forms.ValidationError(_("Invalid credentials."))

        # Check if the user is verified
        if not user.is_verified:
            raise forms.ValidationError(_("Email is not verified. Please verify your email first."))

        cleaned_data['user'] = user
        return cleaned_data


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        password_validation.validate_password(password)

        return cleaned_data

    def save(self, commit=True):
        # Manually call create_user instead of saving directly via ModelForm
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        print("FORM SAVED...")
        # Call CustomUserManager's create_user method
        user = CustomUser.objects.create_user(email=email, password=password)

        return user
