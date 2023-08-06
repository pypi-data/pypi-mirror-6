from django.forms import ModelForm

from huron.job_board.models import FreeApplication, Application

class FreeApplicationForm(ModelForm):
    class Meta:
        model = FreeApplication


class ApplicationForm(ModelForm):
    class Meta:
        model = Application