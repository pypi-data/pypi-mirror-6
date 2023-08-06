from django.contrib import admin

"""

.. module:: huron.utils.admin
   :platform: Unix
   :synopsis: Admin utils for Huron

.. moduleauthor:: Thomas Durey <tominardi@gmail.com>

"""


class CKEditorAdmin(admin.ModelAdmin):
    """

    Extends admin.ModelAdmin from Django, add JS Files for CKEditor.

    **How to use it**

    Use it in admin.py instead of admin.ModelAdmin. If you have a RichTextField
    on your model, a CKEditor box will be used to edit it.

    """
    class Media:
        js = ("js/ckeditor/ckeditor.js",
              "js/ckeditor/adapters/django.jquery.js",
              "js/ckeditor/app.textarea.ckeditor.js",)
