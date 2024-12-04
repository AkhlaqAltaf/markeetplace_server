from django.urls import path
from dj_rest_auth.views import LoginView
from .views import LoginView, LogoutView, UserRegistrationView, verify_email

app_name = 'accounts'
urlpatterns = [
    path('login/',LoginView.as_view(),name="login"),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/<str:token>/', verify_email, name='verify_email'),

]
