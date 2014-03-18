# -*- coding: utf-8 -*-
import os
from yls_app.models import *
# 主要用于得到当前一些job的状态
class AjaxHandler(object):
	# 得到某个文件有多少行
	@staticmethod
	def get_file_line_count(file_path):
		return os.popen("wc -l " + file_path).read()

	# 得到已经抓取了多少微博
	@staticmethod
	def get_fetched_count():
		path = 'yls_app/tools/contents'
		return os.popen('ls -l ' + path + '/ | wc -l').read()

	# 得到tokenize了多少
	@staticmethod
	def get_tokenized_count():
		path = 'yls_app/tools/tokenized'
		#assert False, os.getcwd() + path
		return os.popen('ls -l ' + path + '/ | wc -l').read()

	# 得到某个类型任务的状态
	@staticmethod
	def get_tasks(task_type):
		task_lists = Task.objects.all().order_by('-start_time')
		return task_lists

class MeaningfulWordsHandler(object):
	# meaningful words file
	MEANINGFUL_WORDS_FILE = 'yls_app/tools/wbl_80'

	# helper function to read the words
	@staticmethod
	def read_raw_token_file(path=MEANINGFUL_WORDS_FILE):
		f = open(path, 'r')
		token_list = []
		for l in f.readlines():
			l = l.decode('utf-8').replace(u'\r\n', u'')
			l = l.replace(u'\n', u'')
			r = l.split(u' ')
			times = 0
			for i in range(len(r)):
				if r[i].isdigit():
					times = r[i]
					continue
				if times != 0:
					word = r[i]
					break
			token_list.append((word, times))
		f.close()
		return token_list

	# meaningful words 删除
	@staticmethod
	def del_meaningful_word(word):
		original_tokens = MeaningfulWordsHandler.read_raw_token_file()
		f_out = open(MeaningfulWordsHandler.MEANINGFUL_WORDS_FILE,'w')
		for i in original_tokens:
			w, times = i
			if w != word:
				f_out.write((unicode(times) + u' ' + w + u'\n').encode('utf-8'))
		f_out.close()

# Handle LDA 相关
class LDAHandler(object):
	RAW_TOKEN_FILE_NAME = MeaningfulWordsHandler.MEANINGFUL_WORDS_FILE
	PROCESSED_TOKEN_FILE_NAME = RAW_TOKEN_FILE_NAME + '_converted'
	LDA_TOOLS_PATH = 'yls_app/tools/run_lda.py'

	@staticmethod
	def convert_token_format(in_file_name, out_file_name, ):
		t = Task.create_new_convert_token_task(in_file_name, out_file_name)
		try:
			t.task_status = Task.TASK_STATUS_STARTED
			t.save()
			f = open(in_file_name, 'r')
			f_out = open(out_file_name, 'w')
			for l in f.readlines():
				l = l.decode('utf-8').replace(u'\r\n', u'')
				l = l.replace(u'\n', u'')
				r = l.split(u' ')
				times = 0
				for i in range(len(r)):
					if r[i].isdigit():
						times = r[i]
						continue
					if times != 0:
						word = r[i]
						break
				f_out.write((word+u'\r\n').encode('utf-8'))
			f_out.close()
		except Exception,e:
			t.infomation = t.infomation + ' Failed with message:' + e.message
			Task.finish_task(t, False) # Failed
			return
		t.infomation = t.infomation + ' Successful with word numbers of ' + AjaxHandler.get_file_line_count(out_file_name)
		Task.finish_task(t, True) # Succeed

	@staticmethod
	def convert_from_raw_tokenized():
		''' convert 1234\n abc to abc\n from tokened_file
		to tokened_file_converted '''
		LDAHandler.convert_token_format(LDAHandler.RAW_TOKEN_FILE_NAME, LDAHandler.PROCESSED_TOKEN_FILE_NAME)

	@staticmethod
	def can_lda_start():
		pass

	@staticmethod
	def start_lda():
		pass

	@staticmethod
	def view_result():
		''' return {
			'topic1' : [('abc', 0.01), ...],
			'topic2' : [('cdd', 0.165), ...] } '''
		pass
	