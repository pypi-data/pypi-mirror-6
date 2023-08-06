from django.conf.urls import patterns, include, url
from django.contrib import admin

import dpl1_main.testing_app.urls

# admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'DLP.views.testing_app', name='testing_app'),
                       # url(r'^blog/', include('blog.urls')),
                       url(r'^testing/',
                           include(dpl1_main.testing_app.urls, app_name='testing_app'))
)
