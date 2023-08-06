# -*- coding: utf-8 -*-
from django.db.models import ImageField, TextField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import AdminTextareaWidget
"""

.. module:: huron.utils.models
   :platform: Unix
   :synopsis: Some utils stuffs for models

.. moduleauthor:: Thomas Durey <tominardi@gmail.com>

"""


class RichTextField(TextField):
    """
    Same as TextField, but add a *rich-text* class in the html widget.

    To be Use with a rich text Editor, like CKEditor.
    See :py:mod:`huron.utils.admin.CKEditorAdmin`
    """
    def formfield(self, **kwargs):
        attrs = {'class': 'rich-text', }
        defaults = {"widget": AdminTextareaWidget(attrs=attrs)}
        return super(RichTextField, self).formfield(**defaults)


class PngField(ImageField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types.

        Example: ['application/pdf', 'image/jpeg']
        default : image/png

        * max_upload_size - a number indicating the maximum file
          size allowed for upload.

            * 2.5MB - 2621440
            * 5MB - 5242880
            * 10MB - 10485760
            * 20MB - 20971520
            * 50MB - 5242880
            * 100MB 104857600
            * 250MB - 214958080
            * 500MB - 429916160

    """
    def __init__(self, *args, **kwargs):
        self.content_types = 'image/png'
        self.max_upload_size = kwargs.pop("max_upload_size")

        super(PngField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(PngField, self).clean(*args, **kwargs)
        file = data.file
        message = _('Please keep filesize under %(max)s. Current filesize: '
                    '%(cur)s') % {'max': filesizeformat(self.max_upload_size),
                                  'cur': filesizeformat(file._size)}
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(message)
            else:
                raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass

        return data


def has_changed(instance, field, manager='objects'):
    """
    Returns true if a field has changed in a model

    May be used in a model.save() method.

    """

    if not instance.pk:
        return True
    manager = getattr(instance.__class__, manager)
    old = getattr(manager.get(pk=instance.pk), field)
    return not getattr(instance, field) == old
