from django import views
from django.urls import path
from dj_rest_auth.views import LoginView
from src.apps.accounts import views
app_name = 'accounts'
urlpatterns = [
    path('',views.AccountsView.as_view(), name='accounts'),
    path('login/',views.LoginView.as_view(),name="login"),
    path('signup/', views.UserRegistrationView.as_view(), name='signup'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('verify/<str:token>/', views.VerifyEmail.as_view(), name='verify_email'),
    path('forgot-email/', views.ForgotPasswordView.as_view(), name='forgot_email'),
    path('verify-email/<str:email>/', views.VerifyEmail.as_view(), name='verify_email'),
    path('resend-otp/', views.ResendOtp.as_view(), name='resend_otp'),
]
