# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Menu(models.Model):
    name = models.CharField(_(u'Menu name'), max_length=200)
    slug = models.SlugField(_(u'Reference'), max_length=200)
    css_id = models.CharField(_(u'CSS identifier'), max_length=200, blank=True)
    css_class = models.CharField(_(u'CSS classes (comma separated)'),
                                 max_length=200, blank=True)

    class Meta:
        ordering = ['name']

    def get_first_level(self):
        datas = Item.objects.filter(menu=self, parent__isnull=True)
        return datas

    def __unicode__(self):
        return self.name


class Item(models.Model):
    nav_title = models.CharField(_(u'navigation title'), max_length=200)
    url = models.CharField(max_length=256)
    sorting = models.IntegerField(_(u'ordering'))
    parent = models.ForeignKey('self', blank=True, null=True)
    description = models.CharField(_(u'description'), max_length=200, blank=True)
    html_title = models.CharField(_(u'HTML title attribute'), max_length=200,
                                  blank=True)
    css_class = models.CharField(_(u'CSS classes (comma separated)'), max_length=200,
                                  blank=True)
    target_blank = models.BooleanField(_(u"""open link in new window"""))
    menu = models.ForeignKey('Menu')

    def has_childs(self):
        return self.item_set.exists()

    def get_childs(self):
        return self.item_set.all()

    def get_brothers(self):
        if self.parent:
            return self.parent.get_childs()
        else:
            return self

    class Meta:
        ordering = ['parent__id', 'sorting']

    def __unicode__(self):
        return self.nav_title
