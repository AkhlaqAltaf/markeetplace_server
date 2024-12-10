from django.contrib import admin

# Register your models here.

from .models import Category, Product

from .models import Category,  Product, ProductVariant, Media,SubCategory, Tag, ShippingInfo, Review,CountryOrigin

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(CountryOrigin)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(Media)
admin.site.register(Tag)
admin.site.register(ShippingInfo)

admin.site.register(Review)