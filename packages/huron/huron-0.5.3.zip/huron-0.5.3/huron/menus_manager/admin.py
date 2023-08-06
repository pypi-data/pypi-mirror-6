from huron.menus_manager.models import Menu, Item
from django.contrib import admin
from huron.utils.admin import CKEditorAdmin


class ItemInline(admin.StackedInline):
    model = Item
    extra = 5


class MenuAdmin(CKEditorAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Menu, MenuAdmin)
#admin.site.register(Item)