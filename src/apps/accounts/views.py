import random
from django import forms
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser
from marketplace_server import settings
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
    template_name = 'accounts/accounts.html'

    def get(self,request):
        form = CustomLoginForm()
        return render(request, self.template_name,{'signin_form': form})


    def post(self, request):
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('core:home')
        return render(request, self.template_name, {'signin_form': form})


class UserRegistrationView(View):
    template_name = 'accounts/accounts.html'
    def get(self,request):
        form = UserRegistrationForm()
        return render(request, self.template_name,{'signin_form': form})
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('accounts:accounts')
        return render(request, 'accounts/accounts.html', {'signup_form': form})
    

class LogoutView(View):
    def get(self, request):
        logout(request)  # Log out the user
        return redirect('core:home')  # Redirect to /the home page or desired URL


class AccountsView(View):
    template_name = 'accounts/accounts.html'
    def get(self,request):
        sigin_form = CustomLoginForm()
        signup_form = UserRegistrationForm()
        return render(request, self.template_name, {'signin_form': sigin_form, 'signup_form': signup_form })

class ForgotEmailForm(forms.Form):
    email = forms.EmailField()

def Forgot_Email_View(request):
    message = None  # Initialize the message
    message_type = None  # This will store whether the message is "success" or "error"
    verification_code_sent = False  # Track if the verification code has been sent
    verification_successful = False  # Track if the verification code is correct
    attempts_left = 3  # Set the number of attempts allowed for entering the verification code
    new_password_form = False  # Track if we are showing the new password form

    form = ForgotEmailForm()  # Initialize the form here so it's always available

    # Handle POST requests
    if request.method == 'POST':
        if 'email' in request.POST:  # Handle form submission for email
            form = ForgotEmailForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']

                # Check if the email exists in the database
                if not CustomUser.objects.filter(email=email).exists():
                    message = "This email address is not registered."  # Email does not exist
                    message_type = "error"  # Set message type to error
                else:
                    # Generate a 6-digit verification code
                    verification_code = random.randint(100000, 999999)

                    # Save the code in the session
                    request.session['verification_code'] = verification_code
                    request.session['email'] = email
                    # request.session['attempts_left'] = attempts_left  # Store remaining attempts

                    # Send the email
                    subject = "Your Verification Code"
                    message_content = f"Your verification code is {verification_code}. Please use this to reset your password."
                    from_email = settings.DEFAULT_EMAIL_FROM
                    recipient_list = [email]

                    try:
                        send_mail(subject, message_content, from_email, recipient_list)
                        message = "A verification code has been sent to your email."  # Set the success message
                        message_type = "success"  # Set message type to success
                        verification_code_sent = True  # Set verification code sent to true
                    except Exception as e:
                        message = f"An error occurred: {str(e)}"  # Set the error message
                        message_type = "error"  # Set message type to error

        elif 'verification_code' in request.POST:  # Handle verification code submission
            entered_code = request.POST.get('verification_code')

            # Retrieve the verification code from the session
            stored_code = request.session.get('verification_code')
            # attempts_left = request.session.get('attempts_left', 3)

            if entered_code and str(entered_code) == str(stored_code):
                # Correct code, allow password reset
                verification_successful = True
                message = "Verification successful. You can now reset your password."
                message_type = "success"
                new_password_form = True  # Show the new password form
            else:
                # Incorrect code
                # attempts_left -= 1
                # request.session['attempts_left'] = attempts_left  # Update attempts left

                if attempts_left > 0:
                    message = f"Invalid verification code."
                    message_type = "error"
                else:
                    # message = "You have exhausted your attempts. Please try again later."
                    message_type = "error"
                    # Optionally, you can lock the process or disable the button here
                    verification_code_sent = False  # Lock out the user

        elif 'new_password' in request.POST:  # Handle new password submission
            # Retrieve and process the submitted form data for new password
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # Check if passwords match
            if new_password == confirm_password:
                try:
                    # Retrieve the user based on the email stored in the session
                    email = request.session.get('email')
                    user = CustomUser.objects.get(email=email)

                    # Set the new password for the user
                    user.set_password(new_password)
                    user.save()

                    # Update success message
                    message = "Password reset successful. You can now log in with your new password."
                    message_type = "success"

                    # Clear session data after successful password update
                    del request.session['verification_code']
                    del request.session['email']
                    # del request.session['attempts_left']

                except CustomUser.DoesNotExist:
                    # Handle case where user does not exist
                    message = "User not found. Please try again."
                    message_type = "error"
            else:
                # If passwords do not match, display an error message
                message = "Passwords do not match. Please try again."
                message_type = "error"

    else:
        form = ForgotEmailForm()  # Initialize the form on GET request

    # Re-render the template with the form, message, message type, and verification code sent flag
    return render(request, 'accounts/forgetEmail.html', {
        'form': form,
        'message': message,
        'message_type': message_type,
        'verification_code_sent': verification_code_sent,
        'verification_successful': verification_successful,
        # 'attempts_left': attempts_left,
        'new_password_form': new_password_form,  # Pass flag for new password form
    })