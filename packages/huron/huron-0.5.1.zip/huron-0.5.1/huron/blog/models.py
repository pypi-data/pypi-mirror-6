# -- coding:utf-8 --
from django.db import models
from django.template.defaultfilters import slugify
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.translation import ugettext_lazy as _

from cStringIO import StringIO

from PIL import Image as PILImage
from PIL import ImageOps

from huron.utils.models import has_changed, RichTextField


class Category(models.Model):
    """

    Category model for blog entries

    Fields available:

    * title - str
    * slug - str

    .. note::
        Those fields are available for a Category object and can be called in
        templates

    """
    title = models.CharField(_(u'title'), max_length=100)
    slug = models.SlugField(_(u'slug'), max_length=100, unique=True)

    def get_absolute_url(self):
        """

        Return permalink of the category

        .. warning::
            This URL is hardcoded. It should be resolved by Django. (see bug #1)

        """
        return "/blog/%s/" % self.slug

    def __unicode__(self):
        return self.title


class Post(models.Model):
    """

    Post model of blog application

    Fields available:

    * title - str
    * image - image
    * short_desc - str
    * article - str 
    * slug - str
    * rec_date - date
    * pub_date - date
    * last_mod - date
    * published - bool
    * categories - manytomany

    .. note::
        Those fields are available for a Post object and can be called in
        templates

    """
    title = models.CharField(_(u'title'), max_length=100)
    image = models.ImageField(_(u'main image'), upload_to=u'blog',
                              blank=True, null=True)
    short_desc = RichTextField(_(u'short description'), )
    article = RichTextField(_(u'article'), )
    slug = models.SlugField(_(u'slug'), max_length=100, unique=True)
    rec_date = models.DateField(_(u'recording date'), auto_now_add=True)
    pub_date = models.DateTimeField(_(u'publication date'))
    last_mod = models.DateTimeField(_(u'last modification date'), auto_now=True)
    published = models.BooleanField(_(u'published'), default=False)
    categories = models.ManyToManyField(Category)

    def save(self, *args, **kwargs):
        if has_changed(self, 'image'):
            if self.image:
                filename = slugify(self.title)
                image = PILImage.open(self.image.file)

                if image.mode not in ('L', 'RGB'):
                    image = image.convert('RGB')

                imagefit = ImageOps.fit(image, (340, 220), PILImage.ANTIALIAS)

                temp = StringIO()
                imagefit.save(temp, 'jpeg')
                temp.seek(0)

                self.image.save(
                    filename+'.jpg',
                    SimpleUploadedFile('temp', temp.read()),
                    save=False)

        # Save this Post instance
        super(Post, self).save()
        try:
            ping_google()
        except Exception:
            # Bare 'except' because we could get a variety
            # of HTTP-related exceptions.
            pass

    def get_absolute_url(self):
        """

        Return permalink of the post object

        .. warning::
            This URL is hardcoded. It should be resolved by Django. (see bug #1)

        """
        return "/blog/%s/%s/%s/%s/" % (self.pub_date.day,
                                   self.pub_date.month,
                                   self.pub_date.year,
                                   self.slug)

    def __unicode__(self):
        return self.title
