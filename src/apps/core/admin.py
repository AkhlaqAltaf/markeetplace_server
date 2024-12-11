from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.admin import AdminSite

# Custom Admin Site class
class MyAdminSite(AdminSite):
    site_header = 'Habba-Wa-Jumla'
    site_title = 'Habba-Wa-Jumla Admin Dashboard'
    index_title = 'Welcome to Habba-Wa-Jumla Admin Panel'

# Create an instance of the custom admin site
admin_site = MyAdminSite(name='myadmin')