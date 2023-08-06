from django import forms


class QuizzForm(forms.Form):
    huron_quizz = forms.IntegerField()
