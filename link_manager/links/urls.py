from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('links.views',
    (r'^$', 'home'),
    (r'^ignore_site/(\d+)$', 'ignore_site'),
    (r'^keep/(\d+)$', 'keep'),
    (r'^cleanup$', 'cleanup'),
)
