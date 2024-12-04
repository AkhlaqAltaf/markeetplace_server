from django.shortcuts import redirect, render
from django.views import View

from src.apps.whisper.main import Mailing
from src.apps.accounts.forms import CustomLoginForm, UserRegistrationForm
from django.contrib.auth import login , logout
from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousOperation
from django.core import signing



def verify_email(request, token):
    try:
        # Attempt to decode the token
        data = signing.loads(token, salt='email-verification', max_age=3600)  # Token expires in 1 hour
        user_id = data.get('user_id')

        # Get the user from the database
        user = get_user_model().objects.get(id=user_id)

        # Mark the user as verified
        user.is_verified = True
        user.save()

        return redirect('core:home')  # Redirect to home page after successful verification

    except signing.SignatureExpired:
        # Token expired
        return render(request, 'accounts/verification_failed.html', {'error': 'Verification link has expired.'})

    except (signing.BadSignature, get_user_model().DoesNotExist):
        # Invalid token or user doesn't exist
        raise SuspiciousOperation("Invalid verification link.")
    


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        form = CustomLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('core:home')

        return render(request, self.template_name, {'form': form})
  




class UserRegistrationView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('accounts:login')  

        return render(request, self.template_name, {'form': form})
    

class LogoutView(View):
    def get(self, request):
        logout(request)  # Log out the user
        return redirect('core:home')  # Redirect to the home page or desired URL