from django.contrib import admin
from huron.paypal.models import PaypalConfig, PaypalOrder


class PaypalConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'brand_name')


class PaypalOrderAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_amount', 'ship_name', 'transaction_id')
    search_fields = ['ship_name', 'transaction_id', 'token']


admin.site.register(PaypalConfig, PaypalConfigAdmin)
admin.site.register(PaypalOrder, PaypalOrderAdmin)