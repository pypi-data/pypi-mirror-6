from django.contrib.sitemaps import Sitemap
from simple_news import get_latest_news


class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6

    def items(self):
        return get_latest_news

    def lastmod(self, obj):
        return obj.date_lastedit
