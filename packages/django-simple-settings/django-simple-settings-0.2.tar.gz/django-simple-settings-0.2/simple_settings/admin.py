from django.contrib import admin

from .models import Settings


class SettingsAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', ]
    search_fields = ['key', 'value']

admin.site.register(Settings, SettingsAdmin)