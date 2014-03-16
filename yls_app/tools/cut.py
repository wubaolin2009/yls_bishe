# -*- coding: utf-8 -*-
import os
import jieba

# constant variables
root_dir = "/home/willw/bishe_weibo_tengxun/contents/"
FILTER_TEST_FILE = r'/home/willw/bishe_weibo_tengxun/stop.txt'
FILTER_FILE = FILTER_TEST_FILE
OUT_TOKENIZED_FOLDER = "/home/willw/bishe_weibo_tengxun/tokenized/"

# filter the meaningless token
class FilterMeaningless(object):
    def __init__(self, file_name):
        a = open(file_name,'r')
        self.tokens = set()
        for token in a.readlines():
            #print [token.decode('gbk')]
            self.tokens.add(token.decode('gbk').replace('\r\n',''))

    def valid(self, one_token):
        #print type(one_token)
        #print [one_token]
        return one_token not in self.tokens

# filter the characters not Chinese nor English
class FilterNoCharacter(object):
    def __init__(self):
        pass

    def valid(self, one_token):
        def is_chinese(uchar):
            if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
                return True
            else:
                return False

        def is_alphabet(uchar):
            if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
                return True
            else:
                return False

        return all(map(is_chinese,one_token)) or all(map(is_alphabet,one_token))

class EliminateURL(object):
    @staticmethod
    def get_processed_text(text):
        first_a = text.find('<a href=')
        while first_a != -1:
            last_a = text.find('/a>', first_a)
            new_text = text[0:first_a] + text[last_a+3:]
            first_a = new_text.find('<a href=')
            text = new_text
        return text

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

test_filter()

g_filter = FilterMeaningless(FILTER_TEST_FILE)
g_filter2 = FilterNoCharacter()

for a,b,f in os.walk(root_dir):
    all_files = f
    count = 0
    for file_name in f:
        print 'processing' + file_name + " " + str(count)
        count += 1
        if os.path.exists(OUT_TOKENIZED_FOLDER + file_name + '.tok'):
            continue

        to_cut = []
        try:
            for line in open(root_dir + file_name, 'r').readlines():
                context = line.split('!!!@#')[0]
                context = EliminateURL.get_processed_text(context.decode('utf-8'))
                to_cut.append(context)
        except Exception,e:
            continue
        #to_cut = [u'来这里，一战成神！ �已开通腾讯首款3D动作团队竞技网游@SM 的首测资格']
        f = open(OUT_TOKENIZED_FOLDER + file_name + '.tok', 'w')
        for m in to_cut:
            #print '=========', m
            seg_list = jieba.cut(m, cut_all=False)
            for m in seg_list:
                if g_filter.valid(m) and g_filter2.valid(m):
                    #print m
                    f.write((m + u'\r\n').encode('utf-8'))