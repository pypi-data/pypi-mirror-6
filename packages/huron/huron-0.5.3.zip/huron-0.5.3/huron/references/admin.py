from huron.references.models import Reference
from django.contrib import admin
from huron.utils.admin import CKEditorAdmin


class ReferenceAdmin(CKEditorAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Reference, ReferenceAdmin)
