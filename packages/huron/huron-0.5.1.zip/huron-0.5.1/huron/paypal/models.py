# -*- coding: utf-8 -*-
from django.db import models
import urllib
from datetime import datetime


class PaypalConfig(models.Model):
    CURRENCYCODES = (
        ('EUR', 'EUR (€)'),
        ('USD', 'USD ($)')
    )
    LOCALECODES = (
        ('FR', 'France'),
        ('US', 'United States'),
        ('BE', 'Belgium'),
        ('DE', 'Germany'),
        ('ES', 'Spain')
    )
    name = models.CharField(max_length=100, default='default')
    version = models.CharField(max_length=6, default='63.0')
    user = models.CharField(max_length=100)
    pwd = models.CharField(max_length=100)
    signature = models.CharField(max_length=255)
    cancel_url = models.URLField()
    return_url = models.URLField()
    currency_code = models.CharField(max_length=3, choices=CURRENCYCODES)
    locale_code = models.CharField(max_length=100,
                                   default='FR', blank=True,
                                   choices=LOCALECODES)
    hdr_img = models.CharField(max_length=100, blank=True)
    pay_flow_color = models.CharField(max_length=6, blank=True)
    cart_border_color = models.CharField(max_length=6, blank=True)
    brand_name = models.CharField(max_length=127, blank=True)

    def get_url(self, datas, method):
        urn = 'https://api-3t.sandbox.paypal.com/nvp?'
        args = {
            'METHOD': method,
            'VERSION': self.version,
            'USER': self.user,
            'PWD': self.pwd,
            'SIGNATURE': self.signature
        }
        if(method == 'setExpressCheckout'):
            _args = {
                'CANCELURL': self.cancel_url,
                'RETURNURL': self.return_url,
                'LOCALECODE': self.locale_code,
                'HDRIMG': self.hdr_img,
                'PAYFLOWCOLOR': self.pay_flow_color,
                'CARTBORDERCOLOR': self.cart_border_color,
                'BRANDNAME': self.brand_name,
                'PAYMENTREQUEST_0_CURRENCYCODE': self.currency_code,
            }
            args = dict(args.items() + _args.items())
        args = dict(args.items() + datas.items())
        return {
            'url': urn,
            'datas': urllib.urlencode(args)
        }
    
    class Meta:
        ordering = ["name"]
        verbose_name = u"Configuration Paypal"
        verbose_name_plural = u"Configurations Paypal"


class PaypalOrder(models.Model):
    token = models.CharField(max_length=127)
    transaction_id = models.CharField(max_length=127, verbose_name="Code de transaction")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2
                                       , verbose_name="Prix payé")
    ship_name = models.CharField(max_length=255, verbose_name="Nom du client")
    date = models.DateField(default=datetime.now)
    
    class Meta:
        ordering = ["date"]
        verbose_name = u"Commande Paypal"
        verbose_name_plural = u"Commandes Paypal"
