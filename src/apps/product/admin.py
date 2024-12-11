from django.contrib import admin

# Register your models here.

from .models import Category, Product

from .models import Category,  Product, ProductVariant, Media,SubCategory, Tag, ShippingInfo, Review,CountryOrigin
from ..core.admin import admin_site

admin_site.register(Category)
admin_site.register(SubCategory)
admin_site.register(CountryOrigin)
admin_site.register(Product)
admin_site.register(ProductVariant)
admin_site.register(Media)
admin_site.register(Tag)
admin_site.register(ShippingInfo)

admin_site.register(Review)