from huron.simple_medias_manager.models import File, Image
from django.contrib import admin


class FilesAdmin(admin.ModelAdmin):
    list_display = ('the_file', 'name', 'date_upload', 'date_rec')


class ImagesAdmin(admin.ModelAdmin):
    list_display = ('admin_thumbnail', 'name', 'date_rec',
                    'admin_original_link')
    class Media:
        js = ("js/colorbox/jquery.colorbox-min.js",
              "js/colorbox/app.colorbox.js",)
        css = {
             'all': ('js/colorbox/colorbox.css',)
        }


admin.site.register(File, FilesAdmin)
admin.site.register(Image, ImagesAdmin)
