from django import views
from django.urls import path
from dj_rest_auth.views import LoginView
from .views import Forgot_Email_View, LoginView, LogoutView, UserRegistrationView, verify_email, AccountsView

app_name = 'accounts'
urlpatterns = [
    path('',AccountsView.as_view(), name='accounts'),
    path('login/',LoginView.as_view(),name="login"),
    path('signup/', UserRegistrationView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/<str:token>/', verify_email, name='verify_email'),
    path('forgot-email/', Forgot_Email_View, name='forgot_email'),

]
