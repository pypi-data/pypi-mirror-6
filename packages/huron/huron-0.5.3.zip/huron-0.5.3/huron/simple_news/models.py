# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import MaxLengthValidator
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from huron.utils.models import has_changed, RichTextField

from PIL import Image as PILImage
from PIL import ImageOps

from cStringIO import StringIO

from datetime import datetime

"""

.. module:: huron.simple_news.models
   :platform: Unix
   :synopsis: News application for Django - models module

.. moduleauthor:: Thomas Durey <tominardi@gmail.com>

"""


class Category(models.Model):
    """

    Category model of news application.
    Each news can have none, one or many categories.

    Fields available:

    * name - str
    * slug - str
    * description - str
    * parent - date

    .. note::
        Those fields are available for a Category object and can be called in
        templates

    """
    name = models.CharField(_(u'name'), max_length=200)
    slug = models.SlugField(_(u'permalink'), max_length=200, unique=True)
    description = RichTextField(_(u'description'), blank=True)
    parent = models.ForeignKey('self', blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _(u'category')
        verbose_name_plural = _(u'categories')

    def get_absolute_url(self):
        return reverse('simple_news:list_news_categ', None, [self.slug])


class News(models.Model):
    """

    News model of news application

    Fields available:

    * title - str
    * slug - str
    * story - str
    * excerpt - str
    * categories - many to many field
    * date_rec - date
    * date_last_edit - date
    * date_pub - date
    * date_unpub - date
    * image - image
    * published - bool

    .. note::
        Those fields are available for a News object and can be called in
        templates

    """
    title = models.CharField(_(u'title'), max_length=200)
    slug = models.SlugField(_(u'permalink'), max_length=200, unique=True)
    story = RichTextField(_(u'full story'))
    excerpt = RichTextField(_(u'excerpt'),
                               validators=[MaxLengthValidator(800)],
                               blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    date_rec = models.DateTimeField(_(u'creation date'), auto_now_add=True)
    date_last_edit = models.DateTimeField(_(u'last edition date'),
                                          auto_now=True)
    date_pub = models.DateTimeField(_(u'publication date'), blank=True,
                                    null=True)
    date_unpub = models.DateTimeField(_(u'end of publication date'),
                                      blank=True, null=True)
    image = models.ImageField(_(u'featured image'), upload_to='simple_news',
                              blank=True, null=True)
    published = models.BooleanField(_(u'published'), default=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('-date_pub',)
        verbose_name = _(u'news')
        verbose_name_plural = _(u'news')
        get_latest_by = "date_pub"

    def get_absolute_url(self):
        return reverse('simple_news:single_news', None, [self.slug])

    def save(self, *args, **kwargs):
        if has_changed(self, 'image'):
            if self.image:
                if hasattr(settings, 'IMAGE_NEWS_WIDTH'):
                    width = settings.IMAGE_NEWS_WIDTH
                else:
                    width = 220
                if hasattr(settings, 'IMAGE_NEWS_HEIGHT'):
                    height = settings.IMAGE_NEWS_HEIGHT
                else:
                    height = 160
                filename = self.slug
                image = PILImage.open(self.image.file)

                if image.mode not in ('L', 'RGB'):
                    image = image.convert('RGB')

                imagefit = ImageOps.fit(image, (width, height),
                                        PILImage.ANTIALIAS)
                temp = StringIO()
                imagefit.save(temp, 'jpeg')
                temp.seek(0)

                self.image.save(
                    filename+'.jpg',
                    SimpleUploadedFile('temp', temp.read()),
                    save=False)

        if self.date_pub is None:
            self.date_pub = datetime.now()

        super(News, self).save()

