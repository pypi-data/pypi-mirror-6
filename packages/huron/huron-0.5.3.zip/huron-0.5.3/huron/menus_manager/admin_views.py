from django.shortcuts import render
from django.http import HttpResponse
from django.utils import simplejson as json
from django.contrib.auth.decorators import user_passes_test

from huron.menus_manager.models import Menu, Item


@user_passes_test(lambda u: u.has_perm('menus_manager.can_delete_item'))
def del_item(request):
    if request.POST['item-pk'] != '':
        try:
            item = Item.objects.get(pk=request.POST['item-pk'])
            item.delete()
            return HttpResponse(json.dumps('{"status":"ok"}'),
                        content_type="application/json")
        except:
            pass
    return HttpResponse(json.dumps('{"status":"error"}'),
                        content_type="application/json")


@user_passes_test(lambda u: u.has_perm('menus_manager.can_add_item'))
def add_item(request):
    if request.POST['menu-pk'] != '' and request.POST['nav_title'] != '' and request.POST['url'] != '':
        try:
            menu = Menu.objects.get(pk=request.POST['menu-pk'])
            last_item_list = menu.get_first_level().order_by('-sorting')[:1]
            if len(last_item_list) == 0:
                sorting = 0
            else:
                last_item_object = last_item_list[0]
                sorting = last_item_object.sorting + 1
            target_blank = False
            if request.POST['target_blank'] == 'true':
                target_blank= True
            item = Item(
                        nav_title = request.POST['nav_title'],
                        url = request.POST['url'],
                        sorting = sorting,
                        description = request.POST['description'],
                        html_title = request.POST['html_title'],
                        css_class = request.POST['css_class'],
                        target_blank = target_blank,
                        menu = menu,
                        )
            item.save()
            return HttpResponse(json.dumps('{"status":"ok"}'),
                        content_type="application/json")
        except:
            pass
    return HttpResponse(json.dumps('{"status":"error"}'),
                        content_type="application/json")


@user_passes_test(lambda u: u.has_perm('menus_manager.can_change_item'))
def edit_item(request):
    if request.POST['item-pk'] != '' and request.POST['nav_title'] != '' and request.POST['url'] != '':
        try:
            item = Item.objects.get(pk=request.POST['item-pk'])
            target_blank = False
            if request.POST['target_blank'] == 'true':
                target_blank= True
            item.nav_title = request.POST['nav_title']
            item.url = request.POST['url']
            item.description = request.POST['description']
            item.html_title = request.POST['html_title']
            item.css_class = request.POST['css_class']
            item.target_blank = target_blank
            item.save()
            return HttpResponse(json.dumps('{"status":"ok"}'),
                        content_type="application/json")
        except:
            pass
    return HttpResponse(json.dumps('{"status":"error"}'),
                        content_type="application/json")


@user_passes_test(lambda u: u.has_perm('menus_manager.can_change_item'))
def sort_item(request):
    if request.POST['item-pk'] != '' and request.POST['sorting'] != '':
        try:
            item = Item.objects.get(pk=request.POST['item-pk'])
            item.sorting = request.POST['sorting']
            if 'parent' in request.POST:
                parent = Item.objects.get(pk=request.POST['parent'])
                item.parent = parent
            else:
                item.parent = None
            item.save()
            return HttpResponse(json.dumps('{"status":"ok"}'),
                        content_type="application/json")
        except:
            pass
    return HttpResponse(json.dumps('{"status":"error"}'),
                        content_type="application/json")
