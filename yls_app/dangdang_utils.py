__author__ = 'willw'

import Queue
import httplib,urllib
import re
from sgmllib import SGMLParser
import sgmllib
import chardet

start_html = "product.dangdang.com/1215287008.html"

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

def extract_title(html):
    result = re.findall(r"<div class=\"head\" name=\"Title_.*?\">.*<h1>(.*?)<span class=", html, re.S)
    return result[0].decode('GBK')

def extract_detail(html):
    #result = re.findall(r"<div class=\"detail-content\">((<div(.*?)</div>?)*?)</div>", html, re.S)
    #return result[0].decode('GBK')
    listener = URLLister()
    listener.feed(html)
    return listener.name

# extract the cateloge from a given html
def extract_category(html):
    # Major Category
    result = re.findall(r"target=\"_blank\" class=\"domain\" name=\"__Breadcrumb_.*?\"><b class=\"domain\">(.*)</b></a>", html, re.S)
    # Minor Category
    result = re.findall(r'target="_blank" name="__Breadcrumb_.*?">(.*?)</a>', html, re.S)
    return [w.decode('GBK') for w in result]

# get the links from the product page , pointing to another product
def get_other_products(product_id):
    html = fetch_html("product.dangdang.com/multreco.php?product_id=" + str(product_id) )
    results = re.findall(r'product.dangdang.com.*?(\d+).html', html)
    return ["product.dangdang.com/" + a + ".html" for a in list(set(results))]

# general scheme
def run(start, search_level = 3):
    html = fetch_html(start)
    category = extract_category(html)
    price = extract_price(html)
    desc = extract_desc(html)
    # BFS
    product_id = start.split('/')[-1].split('.')[0]
    for next_html in get_other_products(product_id):
        run(next_html)


html = fetch_html(start_html)
print extract_title(html)
for w in extract_category(html):
    print w
for w in extract_detail(html):
    if chardet.detect(w)['encoding'] == 'GB2312':
        print w.decode("gbk")






