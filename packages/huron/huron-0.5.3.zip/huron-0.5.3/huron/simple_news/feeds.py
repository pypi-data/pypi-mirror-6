# -- coding:utf-8 --
from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext as _

from simple_news import get_latest_news

import datetime


class LatestEntriesFeed(Feed):
    title = _("Rss Feed")
    link = "/news/"
    description = _("Last news.")

    def items(self):
        return get_latest_news()

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.story
