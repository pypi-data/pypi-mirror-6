from huron.pages.models import Page
from django.contrib import admin
from huron.utils.admin import CKEditorAdmin


class PageAdmin(CKEditorAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'status', 'see_online',
                    'is_published')
    list_filter = ('status',)
    search_fields = ['title']

admin.site.register(Page, PageAdmin)
