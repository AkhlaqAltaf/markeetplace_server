from django.urls import path

from . import views
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

from .views import  VendorProductListView

app_name = 'vendor'



urlpatterns = [
    path('', views.VendorSiteView.as_view(), name="vendor"),
    path('become-vendor/', views.BecomeVendorView.as_view(), name="become-vendor"),
    path('vendor-admin/', views.VendorAdminView.as_view(), name="vendor-admin"),
    path('edit-vendor/', views.EditVendorView.as_view(), name="edit-vendor"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('<int:vendor_id>/', views.VendorDetailView.as_view(), name="vendor"),
    path('add_product/subcategory/<str:category>/',views.GetSubCategory.as_view(),name="subcategory"),
    path('add_bulk/subcategory/<str:category>/', views.GetSubCategory.as_view(), name="subcategory"),
    path('add_product/', views.AddProductView.as_view(),name="add"),

    path('store-analytics/',views.storeAnalytics,name="store-analytics"),
    path('signup/',views.Register,name="signup"),
    path('create-product/',views.ProductAdd,name="create-product"),
    path('product-list/',views.ProductList,name="product-list"),
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
    path('models/', views.list_models, name='list_models'),
    path('models/create/', views.create_model, name='create_model'),
    path('models/<pk>/download/', views.download_model, name='download_model'),
    path('add_bulk/',views.AddBulkProductsView.as_view(),name='add_bulk')
              ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
