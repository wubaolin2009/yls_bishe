from django.conf.urls import patterns, url

from yls_app import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'crawl_weibo', views.show_crawl_weibo, name='crawl_weibo'),
    url(r'get_qq_token', views.get_qq_token, name='get_qq_token'),
    url(r'fetch_weibo', views.fetch_weibo, name='fetch_weibo'),
)