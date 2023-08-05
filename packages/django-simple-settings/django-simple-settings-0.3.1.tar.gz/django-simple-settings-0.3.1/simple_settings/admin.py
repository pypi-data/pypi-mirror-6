from django.contrib import admin

from .models import Settings


class SettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'value_type']
    search_fields = ['key', 'value']

admin.site.register(Settings, SettingsAdmin)
