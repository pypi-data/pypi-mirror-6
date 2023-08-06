# -*- coding: utf-8 -*-
from django.db import models
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from huron.utils.image import create_thumb
from huron.utils.models import has_changed, RichTextField
from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
from PIL import ImageOps
from django.conf import settings


class Reference(models.Model):
    title = models.CharField(u'Titre', max_length=255)
    slug = models.SlugField(u'Permalien', max_length=255, unique=True)
    description = RichTextField(u'Contenu', blank=True)
    url = models.CharField(u'Lien', max_length=512, blank=True)
    image = models.ImageField(u'Logo', upload_to=u'references')

    class Meta:
        ordering = ["title"]

    def get_permalink(self):
        return reverse('reference.views.reference', args=(self.slug,))

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if has_changed(self, 'image'):
            if self.image:
                if hasattr(settings, 'REFERENCES_WIDTH'):
                    width = settings.REFERENCES_WIDTH
                else:
                    width = 220
                if  hasattr(settings, 'REFERENCES_HEIGHT'):
                    height = settings.REFERENCE_HEIGHT
                else:
                    height = 160
                filename = slugify(self.title)
                image = PILImage.open(self.image.file)

                if image.mode not in ('L', 'RGB'):
                    image = image.convert('RGB')

                imagefit = ImageOps.fit(image, (width, height), PILImage.ANTIALIAS)

                temp = StringIO()
                imagefit.save(temp, 'jpeg')
                temp.seek(0)

                self.image.save(
                    filename+'.jpg',
                    SimpleUploadedFile('temp', temp.read()),
                    save=False)

        # Save this Reference instance
        super(Reference, self).save()
