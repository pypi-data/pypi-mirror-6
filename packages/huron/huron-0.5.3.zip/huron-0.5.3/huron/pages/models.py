# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.html import format_html
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from cStringIO import StringIO

from PIL import Image as PILImage
from PIL import ImageOps

from huron.utils.models import has_changed, RichTextField

from datetime import datetime

"""

.. module:: huron.pages.models
   :platform: Unix
   :synopsis: Pages application for Django - models module

.. moduleauthor:: Thomas Durey <tominardi@gmail.com>

"""


class Page(models.Model):
    """

    Page model of pages application

    Fields available:

    * title - str
    * slug - str
    * status - str
    * creation_date - date
    * last_update - date
    * publish_date - date
    * unpublish_date - date
    * image - image
    * content - str
    * meta_title - str
    * meta_description - str
    * meta_keywords - str

    .. note::
        Those fields are available for a Page object and can be called in
        templates

    """
    STATUS_CHOICES = (('published', _(u'Published')),
                      ('draft', _(u'Draft')),
                      ('waiting', _(u'Waiting')),
                      ('unpublished', _(u'Unpublished')),
                      )
    title = models.CharField(_(u'title'), max_length=255)
    slug = models.SlugField(_(u'permalink'), max_length=255, unique=True)
    status = models.CharField(_(u'status'), max_length=255,
                              choices=STATUS_CHOICES, default='1')
    date_rec = models.DateTimeField(_(u'creation date'), auto_now_add=True)
    date_last_edit = models.DateTimeField(_(u'last edition date'),
                                          auto_now=True)
    date_pub = models.DateTimeField(_(u'publication date'), blank=True,
                                    null=True)
    date_unpub = models.DateTimeField(_(u'end of publication date'),
                                      blank=True, null=True)
    image = models.ImageField(_(u'featured image'), upload_to=u'page',
                              null=True, blank=True)
    content = RichTextField(_(u'content'))
    meta_title = models.CharField(_(u'SEO title'), max_length=255, blank=True)
    meta_description = models.CharField(_(u'SEO description'), max_length=255,
                                        blank=True)
    meta_keywords = models.CharField(_(u'SEO keywords'), max_length=512,
                                     blank=True,
                                     help_text=_(u'comma separated'))

    class Meta:
        ordering = ["title"]
        verbose_name = _(u'page')
        verbose_name_plural = _(u'pages')

    def see_online(self):
        """

        Return html link tag with the absolute url of the page

        :returns: ``<a href="absolute_url">voir sur le site</a>``
        :rtype: str (html tag)

        .. note::
            ``absolute_url`` is obtained with :py:meth:`get_absolute_url`

        """
        return format_html('<a href="{0}">voir sur le site</a>',
                           self.get_absolute_url(),)

    def is_published(self):
        """

        Checked if the page still online

        :returns: True if it's still online, False either
        :rtype: bool

        """
        if self.date_pub < timezone.now() and self.status == 'published':
            if self.date_unpub is not None:
                if self.date_unpub < timezone.now():
                    return False
            return True
        else:
            return False

    def get_absolute_url(self):
        """Return absolute url of the page"""
        return '/%s' % self.slug

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """

        Inheritance from Model.save()
        Checked if the image has changed from the last entry.
        If it's the case, fit the image to the standard size.
        Update the published date to now

        """
        if has_changed(self, 'image'):
            if self.image:
                if hasattr(settings, 'IMAGE_PAGE_WIDTH'):
                    width = settings.IMAGE_PAGE_WIDTH
                else:
                    width = 220
                if hasattr(settings, 'IMAGE_PAGE_HEIGHT'):
                    height = settings.IMAGE_PAGE_HEIGHT
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

        super(Page, self).save()
