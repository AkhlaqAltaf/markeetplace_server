from django.contrib import  admin

from src.apps.whisper.models import HostInfo


@admin.register(HostInfo)
class HostInfoAdmin(admin.ModelAdmin):
    list_filter = ('host_email',)
