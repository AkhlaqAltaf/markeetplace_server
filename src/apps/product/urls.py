from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'product'
urlpatterns = [
    # Category
    # path('categories/', views.CategoryListView.as_view(), name='category-list'),
    # path('category/create/', views.CategoryCreateView.as_view(), name='category-create'),
    # path('category/update/<int:pk>/', views.CategoryUpdateView.as_view(), name='category-update'),
    # path('category/delete/<int:pk>/', views.CategoryDeleteView.as_view(), name='category-delete'),
    #
    # # SubCategory
    # path('subcategories/', views.SubCategoryListView.as_view(), name='subcategory-list'),
    # path('subcategory/create/', views.SubCategoryCreateView.as_view(), name='subcategory-create'),
    # path('subcategory/update/<int:pk>/', views.SubCategoryUpdateView.as_view(), name='subcategory-update'),
    # path('subcategory/delete/<int:pk>/', views.SubCategoryDeleteView.as_view(), name='subcategory-delete'),
    #
    # # Product
    path('', views.ProductListView.as_view(), name='product-list'),
    path('product_create/', views.ProductCreateView.as_view(), name='product-create'),
    path('product_detail/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('product_update/<int:pk>/', views.ProductUpdateView.as_view(), name='product-update'),
    path('product_delete/<int:pk>/', views.ProductDeleteView.as_view(), name='product-delete'),
    
    
    # NEW URLS 
    
    path ('add_product/',views.CreateProduct.as_view(),name="addproduct"),
    path('add_product/getcategories/<str:category>/',views.GetSubCategory.as_view(),name='subcategories')
    # Media (Product media upload)
    # path('media/upload/', views.MediaCreateView.as_view(), name='media-upload'),
    # path('media/delete/<int:pk>/', views.MediaDeleteView.as_view(), name='media-delete'),

    # Shipping Info
    # path('shipping-info/create/', views.ShippingInfoCreateView.as_view(), name='shipping-info-create'),
    # path('shipping-info/update/<int:pk>/', views.ShippingInfoUpdateView.as_view(), name='shipping-info-update'),

    # Review
    # path('reviews/', views.ReviewListView.as_view(), name='review-list'),
    # path('review/create/', views.ReviewCreateView.as_view(), name='review-create'),
    # path('review/delete/<int:pk>/', views.ReviewDeleteView.as_view(), name='review-delete'),

    # Tags (For product tags)
    # path('tags/', views.TagListView.as_view(), name='tag-list'),
    # path('tag/create/', views.TagCreateView.as_view(), name='tag-create'),

    # Product Variants
    # path('product-variants/', views.ProductVariantListView.as_view(), name='product-variant-list'),
    # path('product-variant/create/', views.ProductVariantCreateView.as_view(), name='product-variant-create'),
    # path('product-variant/update/<int:pk>/', views.ProductVariantUpdateView.as_view(), name='product-variant-update'),
    # path('product-variant/delete/<int:pk>/', views.ProductVariantDeleteView.as_view(), name='product-variant-delete'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
