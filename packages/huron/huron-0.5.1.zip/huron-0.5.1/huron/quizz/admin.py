from django.contrib import admin
from django.utils.translation import ugettext as _

from huron.quizz.models import Quizz, QuizzCategory, Answer


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 4


class QuizzAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question', 'category']}),
        (_(u'dates'), {'fields': ['date_unpub']})
    ]
    list_filter = ['category']
    search_fields = ['question']
    inlines = [AnswerInline]


admin.site.register(QuizzCategory)
admin.site.register(Quizz, QuizzAdmin)
