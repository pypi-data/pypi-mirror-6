from huron.settings.models import Setting

def get_settings(request):
    """

    return a dictionnary with every settings store in database.

    .. note::
        This context processor should be added in the setting.py of your
        project

    """
    settings = Setting.objects.all()
    dico = {}
    for obj in settings:
        dico[obj.key] = obj.value
    return {'settings': dico}
