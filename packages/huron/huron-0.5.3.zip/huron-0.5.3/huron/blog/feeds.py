# -- coding:utf-8 --
from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext as _

from blog.models import Post

import datetime


class LatestEntriesFeed(Feed):
    title = _("Rss Feed")
    link = "/blog/"
    description = _("Last entries from blog.")

    def items(self):
        return Post.objects.filter(published=True,
                                   pub_date__lte = datetime.datetime.now).order_by('-pub_date')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.article