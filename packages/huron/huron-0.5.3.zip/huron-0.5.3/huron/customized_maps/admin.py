from huron.customized_maps.models import Map, Marker, Icon
from django.contrib import admin
from huron.utils.admin import CKEditorAdmin


class MarkerInline(admin.StackedInline):
    model = Marker
    extra = 5


class MapAdmin(CKEditorAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = [MarkerInline]


admin.site.register(Map, MapAdmin)
admin.site.register(Icon)
