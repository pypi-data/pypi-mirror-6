# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Setting(models.Model):
    """

    Settings model to add some key in your website.

    Fields available:

    * key - str
    * value - str

    .. note::
        Those fields are available for a Setting object and can be called in
        templates

    """
    key = models.CharField(_(u'key'), max_length=255, unique=True)
    value = models.CharField(_(u'value'), max_length=5000)

    class Meta:
        ordering = ["key"]
        verbose_name = _(u"setting")

    def __unicode__(self):
        return self.key
