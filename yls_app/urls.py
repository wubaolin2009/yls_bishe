
from django.conf.urls import patterns, url

from yls_app import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'crawl_weibo', views.show_crawl_weibo, name='crawl_weibo'),
    url(r'get_qq_token', views.get_qq_token, name='get_qq_token'),
    url(r'fetch_weibo', views.fetch_weibo, name='fetch_weibo'),
    url(r'view_meaningful_words', views.view_meaningful_words, name="view_meaningful_words"),
    url(r'start_cut', views.start_cut, name="start_cut"),
    url(r'start_lda', views.start_lda, name="start_cut"),
    url(r'view_topics', views.view_topics, name="start_cut"),
    url(r'del_meaningful_word', views.del_meaningful_word, name="del_meaningful_word"),
    url(r'convert_to_final_dict', views.convert_to_final_dict, name="convert_to_final_dict"),
    url(r'get_tasks', views.get_tasks, name='get_tasks'),
    url(r'goods_home', views.goods_home, name='goods_home'), # homepage of manipulating goods
    url(r'fetch_relations', views.fetch_relations, name='fetch_relations'),
    url(r'find_goods', views.find_goods, name='find_goods'),
    url(r'show_relations', views.show_relations, name='show_relations'),
    url(r'get_weibo_stats', views.get_weibo_stats, name='get_weibo_stats'),
    url(r'view_goods_category', views.view_goods_category, name='view_goods_category'),
    url(r'view_goods_by_cate', views.view_goods_by_cate, name='view_goods_by_cate'),
    url(r'view_weibouser', views.view_weibouser, name='view_weibouser'),
)
