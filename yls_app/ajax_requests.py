# -*- coding: utf-8 -*-
import os
# 主要用于得到当前一些job的状态
class AjaxHandler(object):
	# 得到已经抓取了多少微博
	@staticmethod
	def get_fetched_count():
		path = 'yls_app/tools/contents'
		return os.popen('ls -l ' + path + '/ | wc -l').read()