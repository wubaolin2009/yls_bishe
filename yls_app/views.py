# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from yls_app import qqweibo_sdk
from ajax_requests import AjaxHandler
from ajax_requests import MeaningfulWordsHandler
import json
from yls_app.models import *
from yls_app.ajax_requests import LDAHandler
from qqweibo_sdk import QQWeiboUtils
from goods import *
import HTMLParser
import at_lda
import matplotlib.pyplot as plt
import gibbs_lda
from dangdang_utils import DangDang
# Create your views here.

def index(request):
	context = {'which_side_bar_to_select': 0,
		'qq_status': get_current_qq_status(request)
	}
	return render(request, 'yls_app/index.html', context)
    # raise Http404
    # poll = get_object_or_404(Poll, pk=poll_id)

# TODO: save the sdk to db and use alternative client ids
def get_qqweibo_client():
	#return qqweibo_sdk.Client.get_client('801486706', 'ccb88ca0bd2d2ab59465abf45818567e', redirect_uri='http://117.121.26.136:12333/yls_app/get_qq_token')
	return qqweibo_sdk.Client('801486704', 'f8a0cb0327d53a71aba609707c3ea239', redirect_uri='http://10.60.37.241:12333/yls_app/get_qq_token')

def show_crawl_weibo(request):
	''' involves 3 phrase
		1. get url then redirect user to that.
		2. get the code and set it to session[qq_code], then redirect it to show_crawl_weibo 2nd times
		3. get the access_token '''
	
	client = get_qqweibo_client()
	status = u'没有登录'
	request.session['qqweibo_authorition_url'] = client.get_authorize_url()	
	# redirected from 'get_qq_token'
	if 'qqweibo_code' in request.session.keys() and not 'qqweibo_access_token' in request.session.keys():
		status = u'得到code'
		try:
			access_token = client.get_access_token_from_code(request.session['qqweibo_code'])
		except Exception,e:
			# retry
			del request.session['qqweibo_code']
			return HttpResponseRedirect('/yls_app/crawl_weibo') 
		request.session['qqweibo_access_token'] = access_token
		client.set_access_token(access_token)
		#QQWeiboUtils.set_current_client(client)
		request.session['user_nick'] = QQWeiboUtils.get_current_userinfo(client,access_token)['nick']
		status = u'已登录'
		print request.session['qqweibo_access_token']
	elif 'qqweibo_code' not in request.session.keys():
		# Do Nothing
		url = client.get_authorize_url()
		# return HttpResponseRedirect(url)
		# assert False, request.session.keys()
	else:
		client.set_access_token(request.session['qqweibo_access_token'])
		status = u'已登录'	

	# Get the tasks status
	tasks = [Task.TYPE_CUT, Task.TYPE_CONVERT_RAW_TOKEN, Task.TYPE_RUNLDA]
	tasks_lists = [ AjaxHandler.get_tasks(t) for t in tasks]

	render_dict = {
				'which_side_bar_to_select': 1, # tengxun weibo selected
				'qq_status': get_current_qq_status(request),
				'is_fetching':False,
				'status':status,				
	}

	#if status == u'已登录':
		# try to find the most recent weibo of the logged in user
		#content = client.statuses.home_timeline.get(format='json', pageflag=0, pagetime=0, reqnum=10, type=0, content=0)
		#render_dict['content'] = content['data']['info'][2]['text']

	return render(request, 'yls_app/show_crawl_weibo.html', render_dict)

# This function can be eliminated and all url handles in craw_weibo
def get_qq_token(request):
	code = request.GET['code']
	request.session['qqweibo_code'] = code	
	return show_crawl_weibo(request) #'/yls_app/crawl_weibo')

def fetch_weibo(request):	
	AjaxHandler.start_fetch_weibos(get_qqweibo_client(), request.session['qqweibo_access_token'])
	return HttpResponseRedirect('/yls_app/crawl_weibo')

# [is_logined_in, login_name if logged else logged_in url]
def get_current_qq_status(request):
	if 'qqweibo_access_token' in request.session.keys() :
		return [True, request.session['user_nick']]
	return [False, get_qqweibo_client().get_authorize_url()]

def view_meaningful_words(request):
	contents = MeaningfulWordsHandler.read_raw_token_file()[0:10]
	return render(request, 'yls_app/show_meaningful_words.html', {
		'contents' : contents,
		'which_side_bar_to_select': 1,
		'qq_status': get_current_qq_status(request)
	})

def del_meaningful_word(request):
	word = request.GET['word']
	payload = {'word': word}
	try:
		MeaningfulWordsHandler.del_meaningful_word(word)
	except Exception,e:
		assert False, e
		payload['word'] = 'SERVER_RET_ERROR'
	return HttpResponse(json.dumps(payload), mimetype="application/json")

def start_cut(request):
	#in_foler = "yls_app/tools/contents/"
	#out_folder = "yls_app/tools/tokenized/"
	LDAHandler.start_cut()
	return HttpResponseRedirect('/yls_app/crawl_weibo')

def start_lda(request):
	tokenized_folder = "yls_app/tools/tokenized/"
	meaningful_words_raw = "yls_app/tools/wbl_80"
	condition, msg = LDAHandler.can_lda_start(tokenized_folder, meaningful_words_raw)
	if condition == False:
		return render(request, 'yls_app/show_message.html', {
		'message' : msg,
		})
	LDAHandler.start_lda(tokenized_folder,meaningful_words_raw)
	return HttpResponseRedirect('/yls_app/crawl_weibo')

def run_at_lda(request):
	at_lda.at_lda()
	return HttpResponseRedirect('/yls_app/crawl_weibo')

def view_topics(request):
#	result = LDAHandler.view_result('yls_app/tools/wbl_80_converted_manual_processed', 60, 20)
	result = gibbs_lda.get_results('yls_app/tools/wbl_80_converted_manual_processed',30,20)

	if result['success'] == 0:
		return render(request, 'yls_app/show_message.html', {
		'message' : result['message'],
		})
	# we split it to 3 columns
	return render(request, 'yls_app/show_topics.html', {
		'which_side_bar_to_select': 1,
		'qq_status': get_current_qq_status(request),
		'topics' : (result['topics'][0::3],result['topics'][1::3],result['topics'][2::3])
		})

def convert_to_final_dict(request):
	LDAHandler.convert_from_raw_tokenized()
	return HttpResponseRedirect('/yls_app/crawl_weibo')


def get_tasks(request):
	task_type = [t[0] for t in Task.TYPE_CHOICES]
	if 'task_type'  in request.GET.keys():
		if request.GET['task_type'] not in task_type:
			raise Http404
		task_type = [request.GET['task_type']]
	return_result = []
	for i in task_type:		
		task_lists = AjaxHandler.get_tasks(i)		
		for t in task_lists:
			if t.task_type != i:
				continue
			t_type = t.task_type.replace('TYPE_','')
			t_status = t.task_status.replace('STATUS_', '')
			t_start = str(t.start_time)
			if len(t_start.split('.')) > 1:
				t_start = t_start.split('.')[0] + '.' + t_start.split('.')[1][0:2]
			t_end = str(t.end_time)
			if len(t_end.split('.')) > 1:
				t_end = t_end.split('.')[0] + '.' + t_end.split('.')[1][0:2]
			return_result.append([t_type, t_status, t_start, t_end, str(t.infomation)])
	return HttpResponse(json.dumps(return_result), mimetype="application/json")

def goods_home(request):
	return render(request, 'yls_app/goods_home.html', {
		'which_side_bar_to_select': 2,
		'qq_status': get_current_qq_status(request),
		'goods_count':AjaxHandler.get_goods_count(),
	})

def fetch_relations(request):
	assert 'qqweibo_access_token' in request.session.keys()
	client = get_qqweibo_client()
	QQWeiboUtils.start_fetch_users(client, request.session['qqweibo_access_token'])
	return HttpResponseRedirect('/yls_app/crawl_weibo')

def find_goods(request):
	''' Ajax request '''
	AjaxHandler.find_goods()
	return HttpResponse(json.dumps({'ret_code':0}), mimetype="application/json")

def show_relations(request):
	relations_jpg = AjaxHandler.get_relations_image()
	return HttpResponseRedirect('/yls_app/crawl_weibo')

def get_weibo_stats(request):
	''' Ajax Request'''
	data = {
		'weibo_user_count':AjaxHandler.get_user_count(),
		'weibo_rel_count':AjaxHandler.get_relations_count(),
		'weibo_count':AjaxHandler.get_weibos_count(),
		'weibo_tokened' :AjaxHandler.get_tokenized_count(),
	}
	return HttpResponse(json.dumps(data), mimetype="application/json")

G_ITEMS_PER_PAGE = 6
def get_start_end_item(page_num, all_counts, ITEMS_PER_PAGE=G_ITEMS_PER_PAGE):
	start_item = (int(page_num) - 1) * ITEMS_PER_PAGE
	end_item = start_item + ITEMS_PER_PAGE
	if end_item > all_counts:
		end_item = all_counts
	return (start_item, end_item)

def get_page_count(all_counts, ITEMS_PER_PAGE = G_ITEMS_PER_PAGE):
	return all_counts//ITEMS_PER_PAGE + 1

def view_goods_category(request):
	page_num = request.GET['page_num'] if 'page_num' in request.GET.keys() else 1

	column_descs = ['image', 'link', 'text']
	table = []
	cates = GoodsCategories.get_all_cates()
	all_counts = len(cates)

	start_item, end_item = get_start_end_item(page_num, all_counts)

	for cat_count in cates[start_item:end_item]:
		image_url = cat_count[1]['image']
		title = cat_count[0]
		counts_cat = '共有' + str(cat_count[1]['count']) + '种商品'
		row = [image_url, title, counts_cat]
		row.append('')
		row.append('/yls_app/view_goods_by_cate?category='+title)
		table.append(row)
	param = {
		'which_side_bar_to_select': 2,
		'column_descs':column_descs,
		'title':u'商品类别',
		'table':table,
		'subtitle': '按商品数排序',
		'page_start':page_num, # only useful for the first time
		'page_count':get_page_count(all_counts),
		'page_url':'/yls_app/view_goods_category',
	}
	return render(request, 'yls_app/general_view.html',param)

def view_goods_by_cate(request):
	html_parser = HTMLParser.HTMLParser()
	category = request.GET['category']
	page_num = request.GET['page_num'] if 'page_num' in request.GET.keys() else 1

	subtitle = request.GET['subtitle'] if 'subtitle' in request.GET.keys() else category
	# table [ left, top, bottom, 'link' if left.type=link else '', 'link' if top.type=link else ''
	# left, top, bottom 's type
	column_descs = ['image', 'link', 'text']
	table = []
	if category == 'all':
		all_counts = Goods.objects.all().count()
	else:
		all_counts = Goods.objects.filter(product_category__startswith=category).count()
	start_item, end_item = get_start_end_item(page_num, all_counts)

	item_to_iterate = Goods.objects.filter(product_category__startswith=category)[start_item: end_item]
	if category == 'all':
		item_to_iterate = Goods.objects.all()[start_item:end_item]
	for product in item_to_iterate:
		product_html = product.product_html
		product_name = html_parser.unescape(product.product_name)
		product_cat = product.product_category
		row = [product_html, product_name, product_cat]
		row[0] = product.product_image_url
		row.append('')
		row.append('http://'+product_html) # link to click top title
		table.append(row)
	param = {
		'which_side_bar_to_select': 2,
		'column_descs':column_descs,
		'title':u'商品信息',
		'table':table,
		'subtitle': subtitle,
		'page_start':page_num, # only useful for the first time
		'page_count':get_page_count(all_counts),
		'page_url':'/yls_app/view_goods_by_cate',
		'param1_key':'category',
		'param1_value':category,
	}
	return render(request, 'yls_app/general_view.html',param)

def get_tweet_count(user_name):
	return Tweet.objects.filter(name = user_name).count()

def view_weibouser(request):
	page_num = request.GET['page_num'] if 'page_num' in request.GET.keys() else 1
	recommended = 1 if 'rec' in request.GET.keys() else 0

	column_descs = ['image', 'link', 'text']
	table = []
	all_counts = WeiboUser.objects.all().count()
	start_item, end_item = get_start_end_item(page_num, all_counts)

	# get the latest tweet of a user
	def get_latest_tweet(user):
		if Tweet.objects.filter(name=user.name).exists():
			return Tweet.objects.filter(name=user.name)[0].text
		return '没有抓到微博'

	for user in WeiboUser.objects.all()[start_item:end_item]:
		image_url = user.head + '/40'
		title = user.nick
		title = HTMLParser.HTMLParser().unescape(title)
		last_weibo = get_latest_tweet(user)
		last_weibo = HTMLParser.HTMLParser().unescape(last_weibo)
		last_weibo += u"<br>" +  u' <h6>抓到微博数: %d条</h6>'%(get_tweet_count(user.name))
		row = [image_url, title, last_weibo]
		row.append('')
		#row.append('http://t.qq.com/'+user.name)
		if recommended == 0:
                    row.append('/yls_app/view_weibo_by_user?user_name='+user.name)
		else:
                    row.append('/yls_app/view_weibo_by_user?user_name='+user.name + '&rec=1')
                table.append(row)

	param = {
		'which_side_bar_to_select': 1,
		'column_descs':column_descs,
		'title':u'微博用户',
		'table':table,
		'subtitle': '显示数据库中最近微博',
		'page_start':page_num,
		'page_count': get_page_count(all_counts),
		'page_url':'/yls_app/view_weibouser',
	}
	if recommended == 1:
	    param['subtitle'] = 'Choose the user to reccommend goods'
	return render(request, 'yls_app/general_view.html',param)

def view_weibo_by_user(request):
	page_num = request.GET['page_num'] if 'page_num' in request.GET.keys() else 1
	rec = 1 if 'rec' in request.GET.keys() else 0
	user_name = request.GET['user_name']
	user = WeiboUser.objects.filter(name=user_name)[0]
	column_descs = ['image', 'text', 'text']
	table = []
	all_counts = get_tweet_count(user_name)
	start_item, end_item = get_start_end_item(page_num, all_counts)

	for tweet in Tweet.objects.filter(name=user_name)[start_item:end_item]:
		image_url = user.head + '/40'
		title = user.nick
		weibo = tweet.text
		if tweet.image and len(tweet.image) > 0:
			weibo += u'<br><a id=\'%s\' href=\"%s\"><img width=\"80px\"  height=\"80px\" class=\"media-object\" src=\"%s\" alt=\"微博中的图片\"/></a>'%('preview_img_'+tweet.tweet_id, tweet.image+'/460.jpg', tweet.image+'/120')
		#print tweet.image
		weibo = HTMLParser.HTMLParser().unescape(weibo)
		row = [image_url, title, weibo]
		row.append('')
		row.append('http://t.qq.com/'+user.name)
		table.append(row)
	user_weibo_url = 'http://t.qq.com/'+user.name;
	param = {
		'which_side_bar_to_select': 1,
		'column_descs':column_descs,
		'title':u'微博',
		'table':table,
		'subtitle': u'<a href="%s">%s</a>'%(user_weibo_url,  u'在腾讯微博中查看'),
		'page_start':page_num,
		'page_count': get_page_count(all_counts),
		'page_url':'/yls_app/view_weibo_by_user',
		'param1_key':'user_name',
		'param1_value': user_name,
	}

        param['subtitle'] = u'<a href="%s">%s</a>'%('/yls_app/rec?user='+user_name, u'Recommend')
        param['page_url'] = '/yls_app/view_weibo_by_user?rec=1'

	return render(request, 'yls_app/general_view.html',param)

def clear_topics(request):
	relations_jpg = AjaxHandler.clear_topic_result()
	return HttpResponseRedirect('/yls_app/crawl_weibo')

def perplexity(request):
	gibbs_lda.cal_perplexity('yls_app/tools/wbl_80_converted_manual_processed','yls_app/phi','yls_app/theta',40)
	assert False
	return HttpResponseRedirect('/yls_app/crawl_weibo')

def perplexity_at(request):
	at_lda.calculate_perplexity()
	assert False
	return HttpResponseRedirect('/yls_app/crawl_weibo')

def goods_process(request):
	DangDang.process_goods()
	return HttpResponseRedirect('/yls_app/crawl_weibo')

def goodsgroup_process(request):
	DangDang.process_goods_by_group()
	return HttpResponseRedirect('/yls_app/crawl_weibo')

def view_at_topics(request):
	result = at_lda.get_at_results('yls_app/tools/wbl_80_converted_manual_processed',30,15)

	if result['success'] == 0:
		return render(request, 'yls_app/show_message.html', {
		'message' : result['message'],
		})
	# we split it to 3 columns
	return render(request, 'yls_app/show_topics.html', {
		'which_side_bar_to_select': 1,
		'qq_status': get_current_qq_status(request),
		'topics' : (result['topics'][0::3],result['topics'][1::3],result['topics'][2::3])
		})

def rec(request):
	''' the most import function in this project, to reccomend goods to a user'''
	user = request.GET['user']
	results = gibbs_lda.recommend('yls_app/tools/wbl_80_converted_manual_processed',user)
#	results = [[0.3,0.3,0.1,0.22,0.11],[u'WaWa', [0.1,0.1,0.2,0.2,0.4], 0.12 ]]

	# make the temperary image @ yls_app/goods_%d.png
	xx = range(len(results[1][1]))
	for i in range(1,len(results)):
            user,goods = plt.plot(xx,results[0],'r.-',xx, results[i][1],'g.-')
	    user.set_label("user")
	    goods.set_label("Goods")
	    plt.legend(loc='upper right', shadow=True)
	    plt.savefig('yls_app/static/yls_app/temp_img_results/goods_%d.png'%(i) )
	    plt.clf()
	
	return render(request, 'yls_app/rec_goods.html', {
		'which_side_bar_to_select': 1,
		'qq_status': get_current_qq_status(request),
		'user_topic': results[0],
		'goods': results[1:],
		'img_temp': "goods_1.png",
		'title': 'Goods Recommended',
		})

