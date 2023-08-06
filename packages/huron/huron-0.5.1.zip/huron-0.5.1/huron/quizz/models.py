# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import datetime


class QuizzCategory(models.Model):
    name = models.CharField(_(u'name'), max_length=100)

    class Meta:
        ordering = ["name"]
        verbose_name = _(u"category")
        verbose_name_plural = _(u"categories")

    def __unicode__(self):
        return self.name


class Quizz(models.Model):
    question = models.CharField(max_length=255)
    category = models.ForeignKey(QuizzCategory, verbose_name=_(u'category'))
    date_pub = models.DateTimeField(_(u'publication date'),
                                    default=datetime.now)
    date_unpub = models.DateTimeField(_(u'end of publication date'),
                                      blank=True, null=True)

    class Meta:
        ordering = ["date_pub"]
        verbose_name = _(u'quizz')
        verbose_name_plural = _(u'quizz')

    def __unicode__(self):
        return self.question


class Answer(models.Model):
    quizz = models.ForeignKey(Quizz, verbose_name=_(u'quizz'))
    text = models.CharField(_(u'text'), max_length=255)
    is_good_answer = models.BooleanField(_(u'is the good answer'),
                                         help_text=_(u'must be unique'),
                                         default=False)

    class Meta:
        ordering = ["quizz"]
        verbose_name = _(u'answer')
        verbose_name_plural = _(u'answers')

    def __unicode__(self):
        return self.text
