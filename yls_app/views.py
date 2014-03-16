from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404

# Create your views here.

def index(request):
	context = {'latest_poll_list': [7777,321]}
	return render(request, 'yls_app/index.html', context)
    # raise Http404
    # poll = get_object_or_404(Poll, pk=poll_id)

def show_crawl_weibo(request):
	return render(request, 'yls_app/show_crawl_weibo.html', {})