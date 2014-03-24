# -*- coding: utf-8 -*-
__author__ = 'Sequoia Yang'

import Queue
import httplib,urllib
import re
from sgmllib import SGMLParser
import sgmllib
import chardet
from yls_app.models import *
class URLLister(SGMLParser):
    def __init__(self, verbose = 0):
        sgmllib.SGMLParser.__init__(self, verbose)
        self.name = []
        self.current_div_status = 0

    def start_div(self, attrs):
        href = [v for k, v in attrs if k=='class' and v=='descrip']
        if len(href) > 0:
            self.current_div_status += 1
        elif self.current_div_status > 0:
            self.current_div_status += 1
        
    def end_div(self):
        if self.current_div_status > 0:
            self.current_div_status -= 1

    def handle_data(self, text):
        if self.current_div_status > 0:
            self.name.append(text)

class DangDang(object):
    @staticmethod
    def get_start_htmls():
        return ["product.dangdang.com/1215287008.html"]

    @staticmethod
    def fetch_html(page):
        # extract a valid address
        host = page.split('/')[0]
        url = '/'.join(page.split('/')[1:]) if len( page.split('/')) > 1 else ''
        headers = {"Host": host,
                   "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5",
                    "Accept": "text/plain"}

        http_client = httplib.HTTPConnection(host)
        http_client.request('GET', '/' + url, headers=headers )
        response = http_client.getresponse()
        #print response.status, host + '/' + url
        if response.status != 200:
            response.read()
            return None
        s = response.read()
        s = s.replace("\r\n"," ")
        return s

    @staticmethod
    def extract_title(html):
        result = re.findall(r"<div class=\"head\" name=\"Title_.*?\">.*<h1>(.*?)<span class=", html, re.S)
        return result[0].decode('GBK')

    @staticmethod
    def extract_detail(html):
        #result = re.findall(r"<div class=\"detail-content\">((<div(.*?)</div>?)*?)</div>", html, re.S)
        #return result[0].decode('GBK')
        listener = URLLister()
        listener.feed(html)
        return listener.name

    # extract the cateloge from a given html
    @staticmethod
    def extract_category(html):
        # Major Category
        result = re.findall(r"target=\"_blank\" class=\"domain\" name=\"__Breadcrumb_.*?\"><b class=\"domain\">(.*)</b></a>", html, re.S)
        # Minor Category
        result = re.findall(r'target="_blank" name="__Breadcrumb_.*?">(.*?)</a>', html, re.S)
        return u'--'.join([w.decode('GBK') for w in result])

    # get the links from the product page , pointing to another product
    @staticmethod
    def get_other_products(product_id):
        html = DangDang.fetch_html("product.dangdang.com/multreco.php?product_id=" + str(product_id) )
        results = re.findall(r'product.dangdang.com.*?(\d+).html', html)
        return ["product.dangdang.com/" + a + ".html" for a in list(set(results))]

    # general scheme
    @staticmethod
    def find_goods(start, the_level = 1, search_level = 3):
        if the_level > search_level:
            return
        html = DangDang.fetch_html(start)
        category = DangDang.extract_category(html)
        title = DangDang.extract_title(html)
        # build the model of goods
        goods = Goods()
        goods.product_html = start
        goods.product_name = title
        goods.product_category = category
        goods.save()
        # BFS
        product_id = start.split('/')[-1].split('.')[0]
        other_products = get_other_products(product_id)
        random.shuffle(other_products)
        for next_html in other_products(product_id):
            if len(Goods.objects.filter(product_html=next_html)) == 0:
                find_goods(next_html, the_level=the_level + 1)

    # convert all files that were fetched before into My SQL server
    @staticmethod
    def convert_to_mysql(path_file):
        o = open(path_file,'r')
        for m in o.readlines():
            m = m.decode('utf-8')
            m = m.replace(u'\r\n',u'')
            m = m.replace(u'\n',u'')
            try:
                id = m.split('@@!!')[0]
                title = m.split('@@!!')[1].split('##$$')[0]
                cat = m.split('@@!!')[1].split('##$$')[1]
                print id
            except Exception,e:
                continue
            good = Goods()
            good.product_html = 'product.dangdang.com/' + id + '.html'
            good.product_name = title
            try:
                good.product_category = cat
                good.save()
            except Exception,e:
                print e
