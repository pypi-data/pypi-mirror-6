# -*- coding: utf-8 -*-
from django.test import TestCase

from settings.models import Setting

class Setting_test(TestCase):

    def test_unicode(self):
        """function: __unicode__"""
        s = Setting(key=u"test key", value=u"test value")
        self.assertEqual(unicode(s), u"test key")
