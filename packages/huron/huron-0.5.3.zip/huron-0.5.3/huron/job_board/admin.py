from huron.job_board.models import ContractType, Offer, Tag, Application
from django.contrib import admin
from huron.utils.admin import CKEditorAdmin


class TagInline(admin.StackedInline):
    model = Offer.tags.through


class ContactTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('label',)}


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('label',)}


class OfferAdmin(CKEditorAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'reference', 'date_pub', 'date_last_edit',
                    'date_unpub')
    search_fields = ['title']
    list_filter = ('type', 'date_pub', 'date_unpub', 'filled',)
    inlines = [
        TagInline,
    ]
    exclude = ('tags',)


class ApplicationAdmin(CKEditorAdmin):
    search_fields = ['last_name', 'first_name']
    list_display = ('__unicode__', 'first_name', 'last_name', 'offer', 'email')
    list_filter = ('date_apply',)


admin.site.register(ContractType, ContactTypeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(Application, ApplicationAdmin)
