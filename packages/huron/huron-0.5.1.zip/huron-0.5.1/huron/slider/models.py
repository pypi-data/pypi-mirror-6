from django.db import models
from django.template.defaultfilters import slugify
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.translation import ugettext_lazy as _

from huron.utils.models import has_changed, RichTextField

from cStringIO import StringIO

from PIL import Image as PILImage
from PIL import ImageOps

import os


def get_upload_path(instance, filename):
    return os.path.join('slider', instance.slider.slug, filename)


# Create your models here.
class Slider(models.Model):
    name = models.CharField(_(u'name'), max_length=256)
    slug = models.SlugField(_(u'permalink'), unique=True)
    width = models.IntegerField(_(u'width'))
    height = models.IntegerField(_(u'height'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'slideshow')
        verbose_name_plural = _(u'slideshows')


class Slide(models.Model):
    name = models.CharField(_(u'name'), max_length=256)
    image = models.ImageField(_(u'image'), upload_to=get_upload_path)
    ordering = models.IntegerField(_(u'ordering'))
    description = RichTextField(_(u'description'), blank=True)
    url = models.URLField(_(u'link'), help_text=_(u'must be a valid URL'),
                          blank=True)
    slider = models.ForeignKey(Slider, verbose_name=_(u'slideshow'))

    class Meta:
        ordering = ["slider", "ordering"]
        verbose_name = _(u'slide')
        verbose_name_plural = _(u'slides')

    def __unicode__(self):
        return _(u'%(name)s from %(slider)s') % {'name': self.name,
                                                 'slider': self.slider.name}

    def save(self, *args, **kwargs):
        if has_changed(self, 'image'):
            if self.image:
                filename = slugify(self.name)
                image = PILImage.open(self.image.file)

                if image.mode not in ('L', 'RGB'):
                    image = image.convert('RGB')

                imagefit = ImageOps.fit(image,
                                        (self.slider.width,
                                         self.slider.height),
                                        PILImage.ANTIALIAS)

                temp = StringIO()
                imagefit.save(temp, 'jpeg')
                temp.seek(0)

                self.image.save(
                    filename+'.jpg',
                    SimpleUploadedFile('temp', temp.read()),
                    save=False)

        # Save this Matos instance
        super(Slide, self).save()
