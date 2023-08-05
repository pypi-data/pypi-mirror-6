try:
    from django.conf.urls.defaults import patterns, url
except:
    from django.conf.urls import patterns, url

urlpatterns = patterns(
    'moneybookers.views',
    url(r'^$', 'status', name="mb-status"),
)
