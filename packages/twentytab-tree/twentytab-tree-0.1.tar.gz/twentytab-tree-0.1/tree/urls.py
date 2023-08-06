from django.conf.urls import *
from tree.utility import getUrlList


urlpatterns = patterns(
    '',
    (r'^favicon.ico$', 'tree.views.favicon'),
    (r'^sitemap.xml$', 'tree.views.sitemap'),
    (r'^robots.txt$', 'tree.views.robots'),
)
upy_urls, tree_urls = getUrlList()

for app_url in upy_urls:
    urlpatterns += patterns('', app_url)
TREE_URLS = tree_urls