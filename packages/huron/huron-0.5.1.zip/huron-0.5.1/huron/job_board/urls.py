
from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('huron.job_board.views',
    url(r'^$', 'listing', name="listing_offers"),
    url(r'^(?P<slug>[-\w]+)/application/$', 'application', name="application"),
    url(r'^(?P<slug>[-\w]+)$', 'single_offer', name="single_offer"),
    url(r'^free-application/$', 'free_apply', name="free_apply"),

)