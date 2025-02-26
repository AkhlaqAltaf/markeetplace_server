
import random
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.timezone import now

from src.apps.whisper.main import Mailing


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)

        # Delete existing unverified user with the same email
        try:
            existing_user = self.get(email=email)
            if not existing_user.is_verified:
                existing_user.delete()
            else:
                return {
                    'user': existing_user,
                    'status_code': 600,
                    'message': "Email Already Registered"
                }
        except CustomUser.DoesNotExist:
            pass

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        otp = self.generate_otp()
        self.send_verification_email(user, otp)

        # Store OTP temporarily in the database
        OTPVerification.objects.create(user=user, otp=otp, expires_at=now() + timezone.timedelta(minutes=10))

        return user

    def send_verification_email(self, user, otp):
        """
        Sends a verification email with an OTP
        """
        context = {
            'user': user,
            'otp': otp,
        }

        # Use your email sending logic
        mail = Mailing()
        mail.send_email(
            template="mails/verification_email.html",
            to_email=[user.email],
            context=context
        )

    def generate_otp(self):
        """
        Generates a 6-digit OTP
        """
        return random.randint(100000, 999999)

    def validate_otp(self, user, otp):
        """
        Validates the OTP for the user
        """
        print("USER : ")
        print(user)
        print("OTP : ")
        print(otp)
        try:
            otp_record = OTPVerification.objects.get(user=user, otp=otp)
            if otp_record.expires_at < now():
                otp_record.delete()
                return False, "OTP Expired"

            user.is_verified = True
            user.save()
            otp_record.delete()
            return True, "Email Verified Successfully"
        except OTPVerification.DoesNotExist:
            return False, "Invalid OTP"

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


class CustomUser(AbstractBaseUser):
    name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = CustomUserManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class OTPVerification(models.Model):
    """
    Stores OTP for email verification
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="otp_verification")
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP for {self.user.email}"
