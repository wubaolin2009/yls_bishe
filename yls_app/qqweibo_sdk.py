#encoding:utf-8

"""
qq weibo sdk
author:tianyu0915@gmail.com
date:2013-02-06
"""

import json
import urllib
import urllib2
import requests
import Queue
from yls_app.models import *
import chardet

class ClientError(Exception):
    pass

class Client(object):
    base_uri = 'https://open.t.qq.com/cgi-bin/oauth2/'
    api_base_uri = 'https://open.t.qq.com/api/'
    request = requests.session()

    def parseurl(self,urlstr):
        """
        parse the url 
        """
        return dict(urllib2.urlparse.parse_qsl(urlstr))

    @classmethod
    # Deprerated
    def get_client(cls,app_key,app_secret,redirect_uri, response_type='code',forcelogin=True):
        ''' Factorys '''
        if not hasattr(cls,'instance'):
            setattr(cls,'instance',Client(app_key, app_secret, redirect_uri, response_type, forcelogin))
        return cls.instance

    def __init__(self,app_key,app_secret,redirect_uri, response_type='code',forcelogin=True):

        self.app_key       = app_key
        self.app_secret    = app_secret
        self.redirect_uri  = redirect_uri
        self.response_type = response_type
        self.forcelogin    = forcelogin and 'true' or 'false' 

    def get_authorize_url(self):
        params = {'client_id':self.app_key,'response_type':self.response_type,'redirect_uri':self.redirect_uri,'forcelogin':self.forcelogin}
        return self.base_uri + 'authorize?' + urllib.urlencode(params)

    def get_access_token_from_code(self,code=''):
        """
        获取access token并存入
        """
        params = {'client_id':self.app_key,'client_secret':self.app_secret,'grant_type':'authorization_code',
                'code':code,'redirect_uri':self.redirect_uri}
        res_str = self.request.get(self.base_uri+'access_token',params=params).content
        if 'errorCode' in res_str:
            raise ClientError(res_str)

        if self.set_access_token(res_str):
            return res_str

    def set_access_token(self,access_token_str):
        res_dict = self.parseurl(access_token_str)
        for k,v in res_dict.items():
            setattr(self,k,v)
        return True

    def call(self,api_method,call_method='GET', **kwargs):
        params = {'access_token':self.access_token,'openid':self.openid,'oauth_consumer_key':self.app_key,
                'clientip':'127.0.0.1','scope':'all','oauth_version':'2.a'}

        for k in kwargs.keys():
            params[k] = kwargs[k]

        #assert False,params
        
        if call_method == 'GET':
            res = self.request.get(self.api_base_uri+api_method,params=params)
        elif call_method == 'POST':
            res = self.request.get(self.api_base_uri+api_method,params=params)
        #assert False, self.api_base_uri+api_method
        if 'errorCode' in res.content:
            raise ClientError(res.content)
        return json.loads(res.content)

    def __getattr__(self,attr):
        return _CallApi(self,attr)

class _CallApi(object):
    """
    """

    def __init__(self, client, name):
        self._client = client
        self._name = name

    def __getattr__(self, attr):
        name = '%s/%s' % (self._name, attr)
        return _CallApi(self._client, name)

    def get(self, **kwargs):
        return self._client.call(self._name,'GET', **kwargs)

    def post(self):
        return self._client.call(self._name,'POST', **kwargs)

    def __str__(self):
        return '_Callable object<%s>' % self._name

# intergrate some QQ weibo common functions in this class 
class QQWeiboUtils(object):
    @staticmethod
    def get_current_userinfo(client, access_token):
        assert client
        client.set_access_token(access_token)
        user_info = client.user.info.get(format='json')
        # current we only return the user_name
        return user_info['data']

    @staticmethod
    def get_user_model(a_user):
        model_user = WeiboUser()
        model_user.name = a_user['name']
        model_user.nick = a_user['nick']
        model_user.head = a_user['head']
        model_user.sex = a_user['sex']
        model_user.country_code = str(a_user['country_code'])
        model_user.province_code = str(a_user['province_code'])
        model_user.city_code = a_user['city_code']
        model_user.fansnum = a_user['fansnum']
        model_user.idolnum = a_user['idolnum']
        return model_user

    @staticmethod
    def get_all_idollist_of(client, user_name, at_most = 30):
        assert client
        idollist = []
        for i in range( (at_most + 29 )// 30 ):
            try:
                lists = client.friends.user_idollist.get(format='json',requnum=30, startindex=i * 30, name=user_name.name)
            except Exception, e:
                print 'WBL', e
                continue    
            if str(lists['ret']) != '0':
               assert False, "Access Limited!"
               return None
            if not lists['data']['info']:
                continue
            for a_user in lists['data']['info']:
                model_user = QQWeiboUtils.get_user_model(a_user)
                if len(a_user['name']) == 0:
                    continue
                idollist.append(model_user)
            if len(lists['data']['info']) < 30:
                break            
        
        return idollist

    @staticmethod
    def get_user_tweet(weibo):
        model_tweet = Tweet()
        model_tweet.tweet_id = weibo['id']
        model_tweet.text = weibo['text']
        model_tweet.origtext = weibo['origtext']
        model_tweet.count = weibo['count']
        model_tweet.mcount = weibo['mcount']
        if type(weibo['image']) != list:
            model_tweet.image = weibo['image']
        else:
            model_tweet.image = ','.join(weibo['image'])
        model_tweet.name = WeiboUser.objects.filter(name=weibo['name'])[0]        
        return model_tweet

    @staticmethod
    def get_all_tweets_of_user(client, user_name, at_most=280):
        all_weibos = list()
        last_id = 0
        last_page_time = 0
        for i in range( (at_most + 69)//70 ):
            #print '---------------', str(i), last_id, last_page_time
            try:       
                contents = client.statuses.user_timeline.get(formate='json',pageflag=0 if i == 0 else 1, pagetime=last_page_time, reqnum=70, lastid=last_id, name=user_name, type=0, contenttype=0)
                if contents['data'] == None:
                    return all_weibos
                hasnext = contents['data']['hasnext']
                weibos = contents['data']['info']
                if str(contents['ret']) != '0':
                    assert False, "Access Limited!"
                    return None
            except Exception,e:
                print e,'193'
                return all_weibos
            if len(weibos) == 0:
                break
            for m in weibos:
                weibo = QQWeiboUtils.get_user_tweet(m)
                all_weibos.append(weibo)

            if hasnext == 0: #has other contents
                last_id = weibos[-1]['id']
                last_page_time = weibos[-1]['timestamp']
            else:
                break
                    
        return all_weibos

    @staticmethod
    def start_fetch_users(client, access_token):
        ''' start from the currently logged in user '''
        my_name = QQWeiboUtils.get_current_userinfo(client, access_token)
        my_name = QQWeiboUtils.get_user_model(my_name)
        my_name.save()

        q = Queue.Queue()
        q.put(my_name)
        while not q.empty():
            user = q.get()
            print 'processing user:', user.name
            all_that = []
            if not UserIdolList.objects.filter(name=user.name):
                all_that = QQWeiboUtils.get_all_idollist_of(client, user)
                print 'Got number of friends:' + str(len(all_that))
                # first save all users
                for one_friend in all_that:
                    if not WeiboUser.objects.filter(name=one_friend.name):
                        #print 'save', one_friend.nick
                        #print chardet.detect(one_friend.nick)
                        one_friend.save()
                # Save all the relationships
                for one_friend in all_that:
                    if not (UserIdolList.objects.filter(name=user).filter(idol_name=one_friend.name)):
                        l = UserIdolList()
                        l.name = user
                        l.idol_name = WeiboUser.objects.filter(name=one_friend.name)[0]
                        print 'IDOL_NAME', l.idol_name.name, '---', one_friend.name
                        l.save()
            else:
                print 'already exists!'
            for m in all_that:
                if not UserIdolList.objects.filter(name=m.name):
                    q.put(m)
            if q.empty():
                # Fetch start from new ones
                for a_user in WeiboUser.objects.all():
                     if not UserIdolList.objects.filter(name=a_user.name) and len(a_user.name) > 0:
                        q.put(a_user)
                        break
    @staticmethod
    def start_fetch_weibos(client, access_token):
        count = 0
        client.set_access_token(access_token)
        for user in WeiboUser.objects.all():
            #print count, '----processing', user.name
            count += 1
            if count % 500 == 0:
                print '----processing', count
            try:
                if Tweet.objects.filter(name=user.name).exists():
                    continue
            except Exception,e:
                print e,'258'
                continue
            all_weibos = QQWeiboUtils.get_all_tweets_of_user(client, user.name)
            # save them
            for weibo in all_weibos:
                try:
                    weibo.save()
                except Exception, e:
                    print e, 'Save Failed!'


        
        