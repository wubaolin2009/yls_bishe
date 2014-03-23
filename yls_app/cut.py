# -*- coding: utf-8 -*-
import os
import jieba
from yls_app.models import *

# constant variables
FILTER_TEST_FILE = r'yls_app/tools/stop.txt'
#FILTER_FILE = FILTER_TEST_FILE

# filter the meaningless token
class FilterMeaningless(object):
    def __init__(self):
        self.tokens = set()
        for token in StopWords.objects.all():
            #print [token.decode('gbk')]
            self.tokens.add(token.word)

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