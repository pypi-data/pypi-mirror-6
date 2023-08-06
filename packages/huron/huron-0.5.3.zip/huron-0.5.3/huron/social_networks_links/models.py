# -*- coding: utf-8 -*-
from django.db import models
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from huron.utils.models import has_changed
from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
from PIL import ImageOps
from huron.utils.models import PngField
from django.utils.translation import ugettext_lazy as _

class Network(models.Model):
    title = models.CharField(_(u'title'), max_length=255)
    slug = models.SlugField(_(u'permalink'), max_length=255, unique=True,
                                 help_text=_(u'used in urls'))
    url = models.CharField(_(u'link'), max_length=512, blank=True,
                           help_text=_(u'must be a valid url'))
    image = PngField(_(u'logo'), upload_to=u'socialnetworks', blank=True, 
                              null=True, max_upload_size=2621440)
    css_class = models.CharField(_(u'css class'), max_length=255,
                                 help_text=_(u'separated by commas'))

    class Meta:
        ordering = ["title"]

    def get_absolute_url(self):
        return reverse('reference.views.reference', args=(self.slug,))

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if has_changed(self, 'image'):
            if self.image:
                width = 32
                height = 32
                filename = slugify(self.title)
                image = PILImage.open(self.image.file)

                imagefit = ImageOps.fit(image, (width, height), PILImage.ANTIALIAS)

                temp = StringIO()
                imagefit.save(temp, 'png')
                temp.seek(0)

                self.image.save(
                    filename+'.png',
                    SimpleUploadedFile('temp', temp.read()),
                    save=False)

        # Save this Network instance
        super(Network, self).save()
