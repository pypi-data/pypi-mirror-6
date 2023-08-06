from django.conf.urls import patterns, include, url
# from django.views.generic.simple import direct_to_template
from urlbreadcrumbs.tests.views import simple_view

from urlbreadcrumbs import url as burl

test1_urls = patterns('',
                      url(r'^$', simple_view,
                          {'template' : 'urlbreadcrumbs_tests/t1.html'},
                          name='t1home'),
                      burl(r'^aaa/$', simple_view,
                           {'template' : 'urlbreadcrumbs_tests/t1sub.html'},
                           name='t1aaa',
                           verbose_name = "Test1 subpage via custom url function"),
                      )

test2_urls = patterns('',
                      burl(r'^aaa/$', simple_view,
                           {'template' : 'urlbreadcrumbs_tests/t2sub.html'},
                           name='t2aaa',
                           verbose_name="T2 test page"),
                      )


urlpatterns = patterns('',
                       url(r'^$', simple_view,
                           {'template' : 'urlbreadcrumbs_tests/index.html'},
                           name='index'),
                       burl(r'^test1/', include(test1_urls)),
                       url(r'^test2/', include(test2_urls)),
                       )
