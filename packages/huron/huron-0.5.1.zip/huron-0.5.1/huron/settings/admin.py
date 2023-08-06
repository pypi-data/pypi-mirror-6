from huron.settings.models import Setting
from django.contrib import admin
from huron.utils.admin import CKEditorAdmin


class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value',)

admin.site.register(Setting, SettingAdmin)
