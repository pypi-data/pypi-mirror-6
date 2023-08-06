from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from huron.blog.models import Post, Category


def single(request, day, month, year, slug):
    post = get_object_or_404(Post, slug=slug)
    #redirect if not correct url
    if (str(post.pub_date.month) != str(month)
        or str(post.pub_date.day) != str(day)
        or str(post.pub_date.year) != str(year)):
        return redirect(post)

    categories = Category.objects.order_by('title')

    other_posts = Post.objects.exclude(pk=post.pk).order_by('?')[:3]

    return render_to_response('blog/single.html',
                          context_instance=RequestContext(request, {'post':post,
                                                                    'categories': categories,
                                                                    'other_posts': other_posts}))

def listing(request, page, category):
    if category is None:
        posts_list = Post.objects.order_by('-pub_date')
    else:
        posts_list = Post.objects.filter(categories__slug=category).order_by('-pub_date')
    paginator = Paginator(posts_list, 10)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        if (category == None):
            return redirect('/blog/')
        else:
            return redirect('/blog/%s/' % category)
    except EmptyPage:
        if (category == None):
            return redirect('/blog/')
        else:
            return redirect('/blog/%s/' % category)

    categories = Category.objects.order_by('title')

    return render_to_response('blog/index.html',
                          context_instance=RequestContext(request, {"object_list": posts,
                                                                    "categories": categories}))
