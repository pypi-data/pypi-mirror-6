import datetime

from django.shortcuts import render, redirect, get_object_or_404

from huron.job_board.models import Offer
from huron.job_board.forms import FreeApplicationForm, ApplicationForm


def listing(request):
    offers = Offer.objects.filter(pub_date__lte=datetime.date.today(),
                                  expire_date__gte=datetime.date.today())
    return render(request, 'job_board/listing_offers.html', {'offers': offers})

def free_apply(request):
    if request.method == 'POST':
        form = FreeApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = FreeApplicationForm()
    return render(request, "job_board/free_application.html", {
        "form": form,
    })


def application(request, slug):
    offer = get_object_or_404(Offer, slug=slug)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ApplicationForm()
    return render(request, "job_board/application.html", {
        "form": form
    })


def single_offer(request, slug):
    offer = get_object_or_404(Offer, slug=slug)
    return render(request, "job_board/single_offer.html", {
        "offer": offer,
    })
