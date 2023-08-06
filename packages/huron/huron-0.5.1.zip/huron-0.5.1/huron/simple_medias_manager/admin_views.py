from huron.simple_medias_manager.models import Image, File
from django.template import RequestContext
from django.shortcuts import render_to_response


def browse_image(request):
    callback = request.GET['CKEditorFuncNum']
    return render_to_response(
        "admin/simple_medias_manager/browse_image.html",
        {'image_list': Image.objects.all(),
        'callback': callback},
        RequestContext(request, {}),
    )


def browse_files(request):
    callback = request.GET['CKEditorFuncNum']
    return render_to_response(
        "admin/simple_medias_manager/browse_files.html",
        {'file_list': File.objects.all(),
        'callback': callback},
        RequestContext(request, {}),
    )
