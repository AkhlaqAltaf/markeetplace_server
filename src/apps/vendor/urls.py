from django.shortcuts import render
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'vendor'



urlpatterns = [
    path('', views.home, name="home"),
    path('become-vendor/', views.BecomeVendorView.as_view(), name="become-vendor"),
    path('vendor-admin/', views.VendorAdminView.as_view(), name="vendor-admin"),
    path('edit-vendor/', views.EditVendorView.as_view(), name="edit-vendor"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('<int:vendor_id>/', views.VendorDetailView.as_view(), name="vendor"),
    path('test/',views.addProductTest,name="add"),
    
    
    path('store-analytics/',views.storeAnalytics,name="store-analytics"),
    path('account/',views.Account,name="account"),
    path('billing/',views.Billing,name="billing"),
    path('general/',views.General,name="general"),
    path('team/',views.Team,name="team"),
    path('notification/',views.Notification,name="notification"),
    path('secuirity/',views.Secuirity,name="secuirity"),
    path('customers-list/',views.CustomerList,name="customers-list"),
    path('customers-details/',views.CustomerDetails,name="customers-details"),

]
