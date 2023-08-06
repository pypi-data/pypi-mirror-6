# -*- coding: utf-8 -*-
from PIL import Image
from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile
"""

.. module:: huron.utils.image
   :platform: Unix
   :synopsis: Some utils stuffs for images in models

.. moduleauthor:: Thomas Durey <tominardi@gmail.com>

"""


def create_thumb(image, size):
    """
    Returns the image resized to fit inside a box of the given size

    :param image: Original image
    :type image: ImageField
    :param size: size of the resized image
    :type size: tuple
    :returns: image
    :rtype: Image

    """

    image.thumbnail(size, Image.ANTIALIAS)
    temp = StringIO()
    image.save(temp, 'jpeg')
    temp.seek(0)

    return SimpleUploadedFile('temp', temp.read())
