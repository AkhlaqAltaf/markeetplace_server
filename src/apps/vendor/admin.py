from django.contrib import admin
from .models import Vendor

# Register your models here.
# admin.site.register(Vendor)
from django.contrib import admin
from .models import Vendor
from ..core.admin import admin_site

admin_site.register(Vendor)