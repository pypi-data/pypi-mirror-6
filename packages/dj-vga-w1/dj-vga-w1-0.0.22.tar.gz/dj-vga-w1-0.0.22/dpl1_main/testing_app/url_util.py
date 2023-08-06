from django.conf.urls import url
from views import pages_view

test_pages_url = url(r'^tests/(?P<test_id>\d+)/(?P<page_id>\d+)',
                     pages_view,
                     name='pages')