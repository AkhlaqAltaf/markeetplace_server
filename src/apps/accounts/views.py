import random
from django.conf import settings
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.utils import timezone
from django.views import View
from marketplace_server import settings
from src.apps.accounts.forms import CustomLoginForm, UserRegistrationForm
from ..product.views import ForgotEmailForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from .models import CustomUser, OTPVerification




class LoginView(View):
    """LOGIN VIEW """
    template_name = 'accounts/accounts.html'
    def get(self, request):
        form = CustomLoginForm()
        return render(request, self.template_name, {'signin_form': form})
    def post(self, request):
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
        return render(request, self.template_name, {'signin_form': form})


class UserRegistrationView(View):
    """USER REGISTRATION VIEW"""
    template_name = 'accounts/accounts.html'
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, self.template_name, {'signup_form': form})
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:verify_email', email=form.cleaned_data['email'])
        return render(request, self.template_name, {'signup_form': form})



class LogoutView(View):
    """USER LOGOUT VIEW"""
    def get(self, request):
        logout(request)
        return redirect('core:home')


class AccountsView(View):
    """A MAIN VIEW FOR REGISTRATION OR LOGIN"""
    template_name = 'accounts/accounts.html'
    def get(self, request):
        signin_form = CustomLoginForm()
        signup_form = UserRegistrationForm()
        return render(request, self.template_name, {'signin_form': signin_form, 'signup_form': signup_form})


def forgat_password(request):
    message = None
    message_type = None
    verification_code_sent = False
    verification_successful = False
    new_password_form = False
    form = ForgotEmailForm()
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


def verify_email(request,email):
    email = request.POST.get('email')
    otp = request.POST.get('otp')
    try:
        user = CustomUser.objects.get(email=email)
        is_valid, message = CustomUser.objects.validate_otp(user, otp)
        if is_valid:
            user.is_verified = True
            user.save()
            login(request, user)
            messages.success(request, "Your email has been verified. You are now logged in.")
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
        else:
            messages.error(request, message)
    except CustomUser.DoesNotExist:
        messages.error(request, "User does not exist.")

    return render(request, "accounts/verify_email.html", {'email': email})




class ResendOtp(View):
    """
    View for resending the OTP to the user's email.
    """
    def post(self, request):
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_verified:
                messages.info(request, "Email is already verified.")
                return redirect('accounts:login:')

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
