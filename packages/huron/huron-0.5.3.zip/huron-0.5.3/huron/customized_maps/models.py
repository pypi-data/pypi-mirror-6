from django.db import models
from django.template.defaultfilters import slugify
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from huron.utils.models import has_changed
from huron.utils.models import PngField

from cStringIO import StringIO

from PIL import Image as PILImage
from PIL import ImageOps

class Map(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    lat = models.FloatField()
    lng = models.FloatField()

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title


class Icon(models.Model):
    title = models.CharField(max_length=255)
    image = PngField(upload_to='icons', max_upload_size=2621440)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if has_changed(self, 'image'):
            if self.image:
                if hasattr(settings, 'REFERENCES_WIDTH'):
                    width = settings.REFERENCES_WIDTH
                else:
                    width = 32
                if  hasattr(settings, 'REFERENCES_HEIGHT'):
                    height = settings.REFERENCE_HEIGHT
                else:
                    height = 32
                filename = slugify(self.title)
                image = PILImage.open(self.image.file)
                png_info = image.info

                imagefit = ImageOps.fit(image, (width, height), PILImage.ANTIALIAS)

                temp = StringIO()
                imagefit.save(temp, 'png', **png_info)
                temp.seek(0)

                self.image.save(
                    filename+'.png',
                    SimpleUploadedFile('temp', temp.read()),
                    save=False)

        # Save this Matos instance
        super(Icon, self).save()


class Marker(models.Model):
    title = models.CharField(max_length=255)
    map = models.ForeignKey('Map')
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    icon = models.ForeignKey('Icon',blank=True, null=True)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title

    def clean(self, *args, **kwargs):
        from django.core.exceptions import ValidationError
        if (self.address == '' and (self.lat == None or self.lng == None)):
            raise ValidationError(_(u'You need to add lat and lng or adress'))
        super(Marker, self).clean(*args, **kwargs)

    def full_clean(self, *args, **kwargs):
        return self.clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Marker, self).save(*args, **kwargs)
