from tkinter.font import names

from django.urls import path

from . import views
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

from .views import VendorProductListView, RemoveProductView

app_name = 'vendor'



urlpatterns = [
    path('', views.VendorSiteView.as_view(), name="vendor"),

    path('edit-product/<int:product_id>/',views.EditProductView.as_view(), name="edit_product"),
    path('become-vendor/', views.BecomeVendorView.as_view(), name="become-vendor"),
    path('vendor-admin/', views.VendorSiteView.as_view(), name="vendor-admin"),
    path('edit-vendor/', views.EditVendorView.as_view(), name="edit-vendor"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('<int:vendor_id>/', views.VendorDetailView.as_view(), name="vendor"),
    path('add_product/subcategory/<str:category>/',views.GetSubCategory.as_view(),name="subcategory"),
    path('add_bulk/subcategory/<str:category>/', views.GetSubCategory.as_view(), name="subcategorybulk"),
    path('add_product/', views.AddProductView.as_view(),name="add"),

    path('select-offer-type/', views.select_offer_type, name='select_offer_type'),
    path('create-product-offer/', views.create_product_offer, name='create_product_offer'),
    path('create-order-offer/', views.create_order_offer, name='create_order_offer'),

    path('store-analytics/',views.storeAnalytics,name="store-analytics"),
    path('signup/',views.register,name="signup"),
    path('create-product/',views.ProductAdd,name="create-product"),
    path('product-list/',views.ProductList,name="product-list"),
    path('checkout/',views.checkout,name="checkout"),
    path('delete-image/',views.DeleteImageView.as_view(),name="delete-image"),
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
    path('products/', VendorProductListView.as_view(), name='vendor_product_list'),
    path('remove/<int:product_id>/', RemoveProductView.as_view(), name='remove_product'),
    path('product_detail/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),

    path('models/', views.list_models, name='list_models'),
    path('models/create/', views.create_model, name='create_model'),
    path('models/<pk>/download/', views.download_model, name='download_model'),
    path('add_bulk/',views.BulkUploadProductView.as_view(),name='add_bulk'),
    path('register-brand/',views.register_brand , name = 'register-brand'),
              ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
