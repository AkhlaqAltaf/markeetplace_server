from django.contrib.admin import AdminSite
# Custom Admin Site class
class MyAdminSite(AdminSite):
    site_header = 'Haba-Wa-Jumla'
    site_title = 'Haba-Wa-Jumla Admin Dashboard'
    index_title = 'Welcome to Haba-Wa-Jumla Admin Panel'

# Create an instance of the custom admin site
admin_site = MyAdminSite(name='myadmin')

