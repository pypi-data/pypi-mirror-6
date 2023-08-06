# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from huron.utils.image import create_thumb
from huron.utils.models import has_changed

from PIL import Image as PILImage

from os.path import splitext, basename

class File(models.Model):
    the_file = models.FileField(_(u'file'), upload_to='simple_medias_manager')
    name = models.CharField(_(u'name'), max_length=50, blank=True)
    date_upload = models.DateField(_(u'upload date'), auto_now=True)
    description = models.CharField(_(u'description'), max_length=250,
                                   blank=True)
    date_rec = models.DateTimeField(_(u'creation date'), auto_now_add=True)
    date_last_edit = models.DateTimeField(_(u'last edition date'),
                                          auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _(u'file')

    def __unicode__(self):
        return self.name


class Image(models.Model):
    the_image = models.FileField(_(u'file'), upload_to='simple_medias_manager')
    thumbnail = models.FileField(_(u'thumbnail'),
                                 upload_to='simple_medias_manager',
                                 editable=False)
    name = models.CharField(_(u'name'), max_length=50, blank=True)
    description = models.CharField(_(u'description'), max_length=250,
                                   blank=True)
    date_rec = models.DateTimeField(_(u'creation date'), auto_now_add=True)
    date_last_edit = models.DateTimeField(_(u'last edition date'),
                                          auto_now=True)

    def get_miniature(self):
        pass

    class Meta:
        ordering = ["name"]
        verbose_name = _(u"image")
        verbose_name_plural = _(u"images")

    def save(self, *args, **kwargs):
        if has_changed(self, 'the_image'):
            # on va convertir l'image en jpg
            filename, file_ext = splitext(basename(self.the_image.name))
            filename = "%s.jpg" % filename

            image = PILImage.open(self.the_image.file)
            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')

            # on crée le thumbnail
            self.thumbnail.save('_%s' % filename,
                                create_thumb(image, (120, 120)),
                                save=False)

        # Save this photo instance
        super(Image, self).save()

    def admin_thumbnail(self):
        return "<img src=\"%s\" alt=\"\" />" % self.thumbnail.url
    admin_thumbnail.short_description = _(u'Thumbnail')
    admin_thumbnail.allow_tags = True

    def admin_original_link(self):
        helping_text = _(u'Show original')
        return '<a href="%s" class="colorbox">%s</a>' % (self.the_image.url,
                                                         helping_text)
    admin_original_link.short_description = _(u'Original')
    admin_original_link.allow_tags = True

    def __unicode__(self):
        return self.name
