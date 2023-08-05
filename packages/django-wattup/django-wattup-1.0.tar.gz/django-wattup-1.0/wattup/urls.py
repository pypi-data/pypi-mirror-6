from django.conf.urls import patterns, url

from wattup.views import ContactView, thanks

urlpatterns = patterns('',

    url('^contact/$', ContactView.as_view(), name='contact'),
    url('^thanks/$', thanks, name='thanks'),
)
