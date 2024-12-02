from django.contrib import admin
from .models import Vendor

# Register your models here.
# admin.site.register(Vendor)
from django.contrib import admin
from .models import Vendor

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'id_card_number', 'mobile_number', 'verification_status')
    list_filter = ('verification_status', 'created_at')
    search_fields = ('name', 'email', 'id_card_number', 'mobile_number')
