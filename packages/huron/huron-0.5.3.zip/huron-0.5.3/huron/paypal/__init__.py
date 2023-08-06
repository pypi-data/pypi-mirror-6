# -*- coding: utf-8 -*-
from huron.paypal.models import PaypalConfig, PaypalOrder
import urllib2
import urllib


def get_paypal_response(appli_name, datas, method):
    config = PaypalConfig.objects.get(name=appli_name)
    url = config.get_url(datas, method)
    try:
        req = urllib2.Request(url["url"], url["datas"])
        response = urllib2.urlopen(req)
        result = response.read()
        infos = result.split('&')
        settings = {}
        print("#--------- PayPal Request ---------#")
        print (url)
        for info in infos:
            values = info.split('=')
            settings[values[0]] = urllib.unquote(values[1]).decode('ascii',
                                                                   'ignore')
        if settings['ACK'] == 'Success':
            return settings
        else:
            print("Paypal module error : "+settings['L_LONGMESSAGE0'])
            return None
    except:
        print("Paypal module error : Impossible de requeter l'url")
        return None


def do_payment(appli_name, token):
    datas = {
        'TOKEN': token
    }
    details = get_paypal_response(appli_name, datas,
                                  'GetExpressCheckoutDetails')
    if(details is not None):
        datas = dict(datas.items() + details.items())
        payment = get_paypal_response(appli_name, datas,
                                      'DoExpressCheckoutPayment')
        if payment is not None and (payment['PAYMENTINFO_0_PAYMENTSTATUS'] == 'Pending' or payment['PAYMENTINFO_0_PAYMENTSTATUS'] == 'Completed'):
            PaypalOrder.objects.create(token=payment['TOKEN'],
                                       transaction_id=payment['PAYMENTINFO_0_TRANSACTIONID'],
                                       total_amount=payment['PAYMENTINFO_0_AMT'],
                                       ship_name=datas['PAYMENTREQUEST_0_SHIPTONAME'])
            return details
        else:
            return None
    else:
        return None


def get_redirect_url(appli_name, datas):
    token = get_paypal_response(appli_name, datas, 'setExpressCheckout')
    if token is not None and ('TOKEN' in token):
        return 'https://www.sandbox.paypal.com/webscr&cmd=_express-checkout&token='+token['TOKEN']
    else:
        return None
