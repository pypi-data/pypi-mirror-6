# -*- coding: utf-8 -*-
from django.template.loader import get_template
from django.template import RequestContext
from huron.quizz.models import Answer


def answers_list(request, quizz):
    answers = Answer.objects.filter(quizz=quizz)
    datas = {}
    datas["items"] = answers
    return get_template('answers-list.html').render(RequestContext(request, datas))


def quizz_template(request, quizz):
    datas = {}
    datas["answers_list"] = answers_list(request, quizz)
    datas["quizz"] = quizz
    return get_template('quizz.html').render(RequestContext(request, datas))
