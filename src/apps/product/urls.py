from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name = 'product'
urlpatterns = [
    path('search/', views.AllProductsView.as_view(), name="search"),
    path('all/', views.AllProductsView.as_view(), name='all-product'),
    path('category_product/<int:id>/', views.CategoryProductsView.as_view(), name='category-product'),
    path('product_detail/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('product_detail3d/<int:pk>/', views.ProductDetail3DView.as_view(), name='product-detail3d'),
    path('add_product/getsubcategories/<str:category>/', views.GetSubCategory.as_view(), name='subcategories'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)