from django.contrib import admin
from huron.utils.admin import CKEditorAdmin
from huron.widget.models import WidgetRichText, WidgetText

class WidgetRichTextAdmin(CKEditorAdmin):
    search_fields = ['title']

class WidgetTextAdmin(CKEditorAdmin):
    search_fields = ['title']

admin.site.register(WidgetRichText, WidgetRichTextAdmin)
admin.site.register(WidgetText, WidgetTextAdmin)
