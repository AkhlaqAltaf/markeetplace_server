
# Register your models here.

from .models import Category, Product, Offer, LandingPageProduct

from .models import Category,  Product, ProductVariant, Media,SubCategory,TopPageProduct, Tag, ShippingInfo, Review , OrderOffer , ProductOffer
from ..core.admin import admin_site
admin_site.register(OrderOffer)
admin_site.register(ProductOffer)
admin_site.register(Category)
admin_site.register(SubCategory)
admin_site.register(Product)
admin_site.register(ProductVariant)
admin_site.register(Media)
admin_site.register(Tag)
admin_site.register(ShippingInfo)
admin_site.register(TopPageProduct)
admin_site.register(Review)
admin_site.register(Offer)
admin_site.register(LandingPageProduct)