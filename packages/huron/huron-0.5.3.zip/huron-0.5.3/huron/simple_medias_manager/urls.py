from django.conf.urls import patterns, url

mediapatterns = patterns('huron.simple_medias_manager.admin_views',
                         # simple_medias_manager
                         url(r'^admin/browser/browse/type/image/?$',
                             'browse_image'),
                         url(r'^admin/browser/browse/type/all/?$',
                             'browse_files'),
                         )
