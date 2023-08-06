# -*- coding: utf-8 -*-
from django import template

register = template.Library()

def get_value(value, key):
    """

    Return a value from a key

    You need to pass the settings as parameter

    .. note:
        Return empty string if key is not in value

    .. note:
        This tag look useless...

    """
    try:
        return value.get(key=key).value
    except:
        return ''

register.filter('get_value', get_value)
