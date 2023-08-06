"""

.. module:: quizz
   :platform: Unix
   :synopsis: Really simple quizz application for Django

.. moduleauthor:: Thomas Durey <tominardi@gmail.com>

This application provides :

* Administration
* Simple templates
* Some helpers

How to install
==============

Firstly, add *huron.quizz* on your INSTALLED_APPS.

Run *syncdb*.

You can now use helpers on your views.

Helpers
=======

"""
from huron.quizz.models import Quizz, Answer
from huron.quizz.views import quizz_template
from huron.quizz.forms import QuizzForm


from datetime import datetime


def get_random_quizz():
    """
        Return a random published quizz
    """
    try:
        quizz = Quizz.objects.filter(date_pub__lte=datetime.today()).order_by('?')[0]
        return quizz
    except:
        return None


def get_quizz_template(request, quizz):
    """
        return HTML code for a quizz, as a Django Template
    """
    if quizz is None:
        quizz = get_random_quizz()
    return quizz_template(request, quizz)


def quizz_is_valid(request):
    """
        check if a quizz answer is valid
    """
    if request.method == 'POST':
        form = QuizzForm(request.POST)
        if form.is_valid():
            id_response = form.cleaned_data['huron_quizz']
            response = Answer.objects.get(id=id_response)
            if response.is_good_answer:
                return True
            else:
                return False
        else:
            return False
    else:
        return None


def quizz_correct_answer(quizz):
    """
        return the correct answer of a quizz

        :param quizz: Quizz object
        :returns: Answer object
    """
    try:
        return Answer.objects.get(quizz=quizz, is_good_answer=True)
    except:
        return None
