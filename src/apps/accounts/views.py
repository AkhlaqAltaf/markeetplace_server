import random
from django import forms
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
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

from ..product.views import ForgotEmailForm


# def verify_email(request, token):
#     try:
#         # Attempt to decode the token
#         data = signing.loads(token, salt='email-verification', max_age=3600)  # Token expires in 1 hour
#         user_id = data.get('user_id')
#
#         # Get the user from the database
#         user = get_user_model().objects.get(id=user_id)
#
#         # Mark the user as verified
#         user.is_verified = True
#         user.save()
#
#         return redirect('core:home')  # Redirect to home page after successful verification
#
#     except signing.SignatureExpired:
#         # Token expired
#         return render(request, 'accounts/verification_failed.html', {'error': 'Verification link has expired.'})
#
#     except (signing.BadSignature, get_user_model().DoesNotExist):
#         # Invalid token or user doesn't exist
#         print(data)
#         raise SuspiciousOperation("Invalid verification link.")


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
            form.save()
            return redirect('accounts:verify_email', email=form.cleaned_data['email'])
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


def Forgot_Email_View(request):
    message = None
    message_type = None
    verification_code_sent = False
    verification_successful = False
    new_password_form = False

    form = ForgotEmailForm()

    if request.method == 'POST':
        if 'email' in request.POST:
            form = ForgotEmailForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                if CustomUser.objects.filter(email=email).exists():
                    verification_code = random.randint(100000, 999999)
                    request.session['verification_code'] = verification_code
                    request.session['email'] = email

                    subject = "Your Verification Code"
                    message_content = f"Your verification code is {verification_code}. Please use this to reset your password."
                    from_email = settings.DEFAULT_EMAIL_FROM
                    recipient_list = [email]

                    try:
                        send_mail(subject, message_content, from_email, recipient_list)
                        message = "A verification code has been sent to your email."
                        message_type = "success"
                        verification_code_sent = True
                    except Exception as e:
                        message = f"An error occurred while sending the email: {str(e)}"
                        message_type = "error"
                else:
                    message = "This email address is not registered."
                    message_type = "error"

        elif 'verification_code' in request.POST:
            entered_code = request.POST.get('verification_code')
            stored_code = request.session.get('verification_code')

            if entered_code and str(entered_code) == str(stored_code):
                verification_successful = True
                message = "Verification successful. You can now reset your password."
                message_type = "success"
                new_password_form = True
            else:
                message = "Invalid verification code. Please try again."
                message_type = "error"

        elif 'new_password' in request.POST:
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password == confirm_password:
                email = request.session.get('email')
                try:
                    user = CustomUser.objects.get(email=email)
                    user.set_password(new_password)
                    user.save()

                    message = "Password reset successful. Please log in with your new password."
                    message_type = "success"

                    del request.session['verification_code']
                    del request.session['email']

                    return redirect('accounts:login')  # Redirect to login page
                except CustomUser.DoesNotExist:
                    message = "User not found. Please try again."
                    message_type = "error"
            else:
                message = "Passwords do not match. Please try again."
                message_type = "error"

    return render(request, 'accounts/forgetEmail.html', {
        'form': form,
        'message': message,
        'message_type': message_type,
        'verification_code_sent': verification_code_sent,
        'verification_successful': verification_successful,
        'new_password_form': new_password_form,
    })

# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from .models import CustomUser, OTPVerification


def verify_email(request,email):
    """
    View for verifying the user's email with OTP and logging them in directly.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')

        try:
            user = CustomUser.objects.get(email=email)
            is_valid, message = CustomUser.objects.validate_otp(user, otp)
            if is_valid:
                # Mark the user as verified
                user.is_verified = True
                user.save()

                # Log the user in
                login(request, user)

                # Redirect to home page
                messages.success(request, "Your email has been verified. You are now logged in.")
                return redirect('core:home')  # Replace 'home' with your actual home page URL name
            else:
                messages.error(request, message)
        except CustomUser.DoesNotExist:
            messages.error(request, "User does not exist.")

    return render(request, "accounts/verify_email.html", {'email': email})


def resend_otp(request):
    """
    View for resending the OTP to the user's email.
    """
    email = None
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_verified:
                messages.info(request, "Email is already verified.")
                return redirect('login')  # Replace 'login' with your desired redirect URL

            otp = CustomUser.objects.generate_otp()
            OTPVerification.objects.update_or_create(
                user=user,
                defaults={
                    'otp': otp,
                    'expires_at': now() + timezone.timedelta(minutes=10),
                }
            )
            CustomUser.objects.send_verification_email(user, otp)
            messages.success(request, "OTP has been resent to your email.")
        except CustomUser.DoesNotExist:
            messages.error(request, "User does not exist.")

    return redirect('accounts:verify_email',email=email)
