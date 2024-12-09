from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'vendor'


urlpatterns = [
    path('', views.vendors, name="vendors"),
    path('become-vendor/', views.BecomeVendorView.as_view(), name="become-vendor"),
    path('vendor-admin/', views.VendorAdminView.as_view(), name="vendor-admin"),
    path('edit-vendor/', views.EditVendorView.as_view(), name="edit-vendor"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('<int:vendor_id>/', views.VendorDetailView.as_view(), name="vendor"),

]
