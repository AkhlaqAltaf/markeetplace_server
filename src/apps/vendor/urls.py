from django.shortcuts import render
from django.urls import path

from . import views
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static
app_name = 'vendor'



urlpatterns = [
    path('', views.home, name="home"),
    path('become-vendor/', views.BecomeVendorView.as_view(), name="become-vendor"),
    path('vendor-admin/', views.VendorAdminView.as_view(), name="vendor-admin"),
    path('edit-vendor/', views.EditVendorView.as_view(), name="edit-vendor"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('<int:vendor_id>/', views.VendorDetailView.as_view(), name="vendor"),
    path('test/',views.addProductTest,name="add"),
    
    path('add_product/subcategory/<str:category>/',views.GetSubCategory.as_view(),name="subcategory"),
    path('add_product/', views.CreateProduct.as_view(),name="add"),

    # path('add_product_form/subcategory/<str:category>/',views.GetSubCategory.as_view(),name="subcategory"),
    # path('add_product_form/', views.AddProductView.as_view(),name="addproduct"),
    
    # path('add_product_form/', CreateProduct.as_view(), name="addproduct"),

    path('store-analytics/',views.storeAnalytics,name="store-analytics"),
    path('create-product/',views.ProductAdd,name="create-product"),
    path('product-list/',views.ProductList,name="product-list"),
    path('order-list/',views.OrderList,name="order-list"),
    path('order-details/',views.OrderDetails,name="order-details"),
    path('order-status/',views.OrderStatus,name="order-status"),
    path('invoice-list/',views.InvoiceList,name="invoice-list"),
    path('invoice-details/',views.InvoiceDetails,name="invoice-details"),
    path('calender/',views.Calender,name="calender"),
    path('account/',views.Account,name="account"),
    path('billing/',views.Billing,name="billing"),
    path('general/',views.General,name="general"),
    path('team/',views.Team,name="team"),
    path('notification/',views.Notification,name="notification"),
    path('secuirity/',views.Secuirity,name="secuirity"),
    path('customers-list/',views.CustomerList,name="customers-list"),
    path('customers-details/',views.CustomerDetails,name="customers-details"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
