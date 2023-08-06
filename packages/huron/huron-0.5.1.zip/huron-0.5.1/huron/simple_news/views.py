from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse

from huron.simple_news import get_new_by_slug, get_latest_news
from huron.simple_news import get_latest_news_by_category
from huron.simple_news.models import Category


def listing(request, page, cat):
    variables = {}

    if(cat is None):
        news_list = get_latest_news()
    else:
        news_list = get_latest_news_by_category(cat)
        variables['category'] = Category.objects.get(slug=cat)
    paginator = Paginator(news_list, 10)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        if (cat is None):
            return redirect('/actualites/')
        else:
            return redirect('/actualites/%s/' % cat)
    except EmptyPage:
        if (cat is None):
            return redirect('/actualites/')
        else:
            return redirect('/actualites/%s/' % cat)

    categories = Category.objects.order_by('name')

    variables['object_list'] = posts
    variables['categories'] = categories

    return render(request, 'simple_news/index.html', variables)


def single(request, slug):
    post = get_new_by_slug(slug)

    variables = {}
    variables['actu'] = post

    return render(request, 'simple_news/single.html', variables)
