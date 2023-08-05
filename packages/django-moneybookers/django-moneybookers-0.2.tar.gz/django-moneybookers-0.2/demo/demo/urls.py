from django.conf.urls import patterns, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    'demo.views',

    url(r'^moneybookers/cancel/', 'canceled', name='canceled'),
    url(r'^moneybookers/ok/', 'done', name='done'),
    url(r'^$', 'view_with_order', name='view_with_order'),
)
