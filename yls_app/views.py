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


# Create your views here.

def index(request):
	context = {'latest_poll_list': [7777,321]}
	return render(request, 'yls_app/index.html', context)
    # raise Http404
    # poll = get_object_or_404(Poll, pk=poll_id)

def show_crawl_weibo(request):
	''' involves 3 phrase
		1. get url then redirect user to that.
		2. get the code and set it to session[qq_code], then redirect it to show_crawl_weibo 2nd times
		3. get the access_token '''

	# TODO: save the sdk to db and use alternative client ids
	def get_qqweibo_client():
		#return qqweibo_sdk.Client.get_client('801486696', 'c45b2b1afb0eae1e64466f7c9fd36319', redirect_uri='http://10.19.225.80:12333/yls_app/get_qq_token')
		return qqweibo_sdk.Client('801486696', 'c45b2b1afb0eae1e64466f7c9fd36319', redirect_uri='http://10.19.225.80:12333/yls_app/get_qq_token')

	client = get_qqweibo_client()
	status = u'没有登录'
	if 'qqweibo_authorition_url' not in request.session.keys():
		request.session['qqweibo_authorition_url'] = client.get_authorize_url()		
	# redirected from 'get_qq_token'
	elif 'qqweibo_code' in request.session.keys() and not 'qqweibo_access_token' in request.session.keys():
		status = u'得到code'
		try:
			access_token = client.get_access_token_from_code(request.session['qqweibo_code'])
		except Exception:
			# retry
			del request.session['qqweibo_code']
			return HttpResponseRedirect('/yls_app/crawl_weibo') 
		request.session['qqweibo_access_token'] = access_token
		status = u'已登录'
	elif 'qqweibo_code' not in request.session.keys():
		# Do Nothing
		url = client.get_authorize_url()
		# return HttpResponseRedirect(url)
	else:
		client.set_access_token(request.session['qqweibo_access_token'])
		status = u'已登录'

	# Get the tasks status
	tasks = [Task.TYPE_CUT, Task.TYPE_CONVERT_RAW_TOKEN, Task.TYPE_RUNLDA]
	tasks_lists = [ AjaxHandler.get_tasks(t) for t in tasks]	

	render_dict = {
				'is_fetching':False,
				'status':status,
				'is_logged_in': status == u'已登录',
				'qq_login_url': client.get_authorize_url(),
				'fetched_count': AjaxHandler.get_fetched_count(),
				'tokened_count': AjaxHandler.get_tokenized_count(),
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
	return HttpResponseRedirect('/yls_app/crawl_weibo')

def fetch_weibo(request):	
	raise Http404

def view_meaningful_words(request):
	contents = MeaningfulWordsHandler.read_raw_token_file()[0:10]
	return render(request, 'yls_app/show_meaningful_words.html', {
		'contents' : contents,
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
	in_foler = "yls_app/tools/contents/"
	out_folder = "yls_app/tools/tokenized/"
	LDAHandler.start_cut(in_foler, out_folder)
	return HttpResponseRedirect('/yls_app/crawl_weibo')

def start_lda(request):
	raise Http404

def view_topics(request):
	raise Http404

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
			t_start = str(t.start_time).split('.')[0] + '.' + str(t.start_time).split('.')[1][0:2]
			t_end = str(t.end_time).split('.')[0] + '.' + str(t.end_time).split('.')[1][0:2]
			return_result.append([t_type, t_status, t_start, t_end, str(t.infomation)])
	return HttpResponse(json.dumps(return_result), mimetype="application/json")


