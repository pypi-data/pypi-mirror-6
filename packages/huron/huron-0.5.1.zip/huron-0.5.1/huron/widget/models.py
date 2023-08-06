# -*- coding: utf-8 -*-
from django.db import models

from huron.utils.models import RichTextField


class WidgetText(models.Model):
    title = models.CharField(u"Titre", max_length=256)
    content = models.TextField(u"Contenu")
    order = models.IntegerField(u"Ordre")
    position = models.SlugField(u"Position", blank=True)

    class Meta:
        ordering = ["order"]

    def __unicode__(self):
        return self.title


class WidgetRichText(models.Model):
    title = models.CharField(u"Titre", max_length=256)
    content = RichTextField(u"Contenu")
    order = models.IntegerField(u"Ordre")
    position = models.SlugField(u"Position", blank=True)

    class Meta:
        ordering = ["order"]

    def __unicode__(self):
        return self.title
