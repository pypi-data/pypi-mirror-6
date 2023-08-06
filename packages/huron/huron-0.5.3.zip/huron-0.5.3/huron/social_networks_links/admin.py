from huron.social_networks_links.models import Network
from django.contrib import admin
from huron.utils.admin import CKEditorAdmin


class NetworkAdmin(CKEditorAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Network, NetworkAdmin)
