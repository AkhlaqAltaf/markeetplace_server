from django.contrib.admin import AdminSite
class MyAdminSite(AdminSite):
    site_header = 'Haba-Wa-Jumla'
    site_title = 'Haba-Wa-Jumla Admin Dashboard'
    index_title = 'Welcome to Haba-Wa-Jumla Admin Panel'
admin_site = MyAdminSite(name='myadmin')

