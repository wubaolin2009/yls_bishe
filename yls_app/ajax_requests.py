# -*- coding: utf-8 -*-
import os
from yls_app.models import *
from cut import *
import thread
import jieba
from run_lda import LDARunner
from dangdang_utils import DangDang

# 用于分词
class Cutter(object):
    @staticmethod
    def test_filter():
        a = [u'兔纸', u'/', u'</', u'?', u'link']
        f = FilterNoCharacter()
        assert f.valid(a[0]) and f.valid(a[-1])
        assert not (f.valid(a[1]) or f.valid(a[2]) or f.valid(a[3]))

        a = [u'我们', u'不然', u'兔子']
        f = FilterMeaningless(FILTER_TEST_FILE)
        assert not f.valid(a[0])
        assert not f.valid(a[1])
        assert f.valid(a[2])

    @staticmethod
    def test():
        test_filter()

    @staticmethod
    def cut(in_folder, out_folder):
        t = Task.create_new_cut_task(in_folder, out_folder)
        g_filter = FilterMeaningless(FILTER_TEST_FILE)
        g_filter2 = FilterNoCharacter()
        t.status = Task.TASK_STATUS_STARTED
        t.save()
        count = 0
        target = AjaxHandler.get_fetched_count()
        try:
            for a,b,f in os.walk(in_folder):
                all_files = f                
                for file_name in f:
                    print 'processing' + file_name + " " + str(count)
                    count += 1
                    if os.path.exists(out_folder + file_name + '.tok'):
                        continue
                    if count % 100 == 0:
                        t.infomation = "Cutted:" + str(count) + "/" + str(target)
                        t.status = Task.TASK_STATUS_STARTED
                        t.save()

                    to_cut = []
                    try:
                        for line in open(in_folder + file_name, 'r').readlines():
                            context = line.split('!!!@#')[0]
                            context = EliminateURL.get_processed_text(context.decode('utf-8'))
                            to_cut.append(context)
                    except Exception,e:
                        continue
                    #to_cut = [u'来这里，一战成神！ �已开通腾讯首款3D动作团队竞技网游@SM 的首测资格']
                    f = open(out_folder + file_name + '.tok', 'w')
                    for m in to_cut:
                        #print '=========', m
                        seg_list = jieba.cut(m, cut_all=False)
                        for m in seg_list:
                            if g_filter.valid(m) and g_filter2.valid(m):
                                #print m
                                f.write((m + u'\r\n').encode('utf-8'))
                    f.close()
        except Exception,e:
            t.infomation = "Exception:" + e.message
            Task.finish_task(t, False)
            return
        t.infomation = "Successful: Cutted " + str(count) + " files"
        Task.finish_task(t, True)

    @staticmethod
    def start_cut(in_folder, out_folder):
        ''' start the thread of cutting '''
        thread.start_new(Cutter.cut, (in_folder, out_folder))

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

	@staticmethod
	def get_relations():
		ret = {}
		for m in UserIdolList.objects.all():
			me =  m.name.name
			friend = m.idol_name
			if me not in ret.keys():
				ret[me] = [(friend.name, friend.nick, friend.head)]
			else:
				ret[me].append(friend.name, friend.nick, friend.head)
		return ret

	@staticmethod
	def get_user_count():
		return WeiboUser.objects.count()

	@staticmethod
	def get_relations_count():
		return UserIdolList.objects.count()

	@staticmethod
	def get_goods_count():
		return Goods.objects.count()


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
	def start_cut(in_folder, out_folder):
		return Cutter.start_cut(in_folder, out_folder)
		#return Cutter.cut(in_folder, out_folder)

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
	def can_lda_start(tokenized_folder, raw_processed_words_path):
		if AjaxHandler.get_tokenized_count() == 0:
			return (False, "没有分词过！")
		if not os.path.exists(raw_processed_words_path):
			return (False, "没有提取过有意义的词")
		if not os.path.exists(raw_processed_words_path + "_converted"):
			return (False, "没有去掉有意义单词的词频field")
		return True, "可以进行LDA"

	@staticmethod
	def start_lda(tokenized_folder,meaningful_words_raw_path):
		meaningful_words_path = meaningful_words_raw_path + "_converted"
		LDARunner.start_run_lda(tokenized_folder, meaningful_words_path)

	@staticmethod
	def view_result(vocab_file, topic_numbers, word_in_topic):
		return LDARunner.get_result(vocab_file, topic_numbers, word_in_topic)

	@staticmethod
	def find_goods():
		DangDang.find_goods(DangDang.get_start_htmls[0])	