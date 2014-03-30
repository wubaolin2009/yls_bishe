from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
import json
from yls_app.models import *

class GoodsCategories(object):
    '''This class represents goods cates, and used to parse the raw category description in the Database'''
    @staticmethod
    def get_all_cates():
        to_ret = set()
        for product in Goods.objects.all().iterator():
            to_ret.add((GoodsCategories.parse_one_category(product.product_category), product.product_image_url))
        ret_dict = {}
        for product in to_ret:
            if len(product[0][0]) == 0:
                continue
            if product[0][0] in ret_dict.keys():
                ret_dict[product[0][0]]['count'] += 1
            else:
                ret_dict[product[0][0]] = {'count':1, 'image':product[1]}
        convert_list = zip(ret_dict.keys(), ret_dict.values())
        convert_list.sort(reverse=True, key=lambda x:x[1]['count'])
        # print convert_list
        return list(convert_list)

    @staticmethod
    def parse_one_category(str_category):
        ''' from A--B--C to ('A', 'B', 'C') '''
        return tuple(str_category.split(u'--'))


