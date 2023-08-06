from django.conf.urls import patterns, url

urlpatterns = patterns(
    'news.views',
    url(r'^$', 'ArticleList', name='articles_list'),
    url(r'^(?P<slug>[\w-]+)/$', 'ArticleDetail',
        name='articles_detail')
)
