from django.conf.urls.defaults import url, patterns

menupatterns = patterns('',
    url(r'^api-menu/add/item/$', 'huron.menus_manager.admin_views.add_item'),
    url(r'^api-menu/del/item/$', 'huron.menus_manager.admin_views.del_item'),
    url(r'^api-menu/edit/item/$', 'huron.menus_manager.admin_views.edit_item'),
    url(r'^api-menu/sort/item/$', 'huron.menus_manager.admin_views.sort_item'),
)