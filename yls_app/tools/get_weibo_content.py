# simple use
from qqweibo import OAuthHandler, API, JSONParser, ModelParser
from qqweibo.utils import timestamp_to_str
import urllib, urllib2, http_helper
import os
a = OAuthHandler('801486043', 'cd0a763d5f7d8be4f588b0f6f290fb06')
a = OAuthHandler('801486692', '35499dde285b599841fcee05aee4e28b')
a = OAuthHandler('801486694','122efd9274999d8eb06b185501611ca0')
a = OAuthHandler('801486696','c45b2b1afb0eae1e64466f7c9fd36319')
aaaaa = OAuthHandler('801486704','f8a0cb0327d53a71aba609707c3ea239')
aaaaa = OAuthHandler('801486706','ccb88ca0bd2d2ab59465abf45818567e')


# Get the keys of user name
users_dict = dict()
aa = open('relations_new', 'r')
users = aa.readlines()
aa.close()
nicks = dict()
for line in users:
	line = line.replace('\n', '')
	line = line.decode('utf-8')
	user_nick, friend = line.split('::::')
	user,nick = user_nick.split(',')
	nicks[user] = nick
	friend_name, friend_nick = friend.split(',')
	nicks[friend_name] = friend_nick
	if user not in users_dict:
		users_dict[user] = []
	users_dict[user].append(friend_name)

# use this
url = a.get_authorization_url()
print 'authorization url:' + url
verifier = raw_input('PIN: ').strip()
a.get_access_token(verifier)

# or directly use:
#token = 'your token'
#tokenSecret = 'your secret'
#a.setToken(token, tokenSecret)
'''rhhgjkli'''

api = API(a)


start = '''rhhgjkli''' 

def get_weibo_of(user_name, at_most = 350):
	all_weibos = list()
	last_id = 0
	last_page_time = 0
	for i in range( (at_most + 69)//70 ):
		print '---------------', str(i), last_id, last_page_time
		#lists = api.timeline.user(pageflag=1, pagetime=1, requnum=1, lastid=310450115899608, name=user_name, type=0, contenttype=0)
		lists = api.timeline.user(pageflag=0 if i == 0 else 1, pagetime=last_page_time, reqnum=70, lastid=last_id, name=user_name, type=0, contenttype=0)
		null = None
		try:
			contents = eval(lists)
			hasnext = contents['data']['hasnext']
			weibos = contents['data']['info']
		except Exception,e:
			return all_weibos

		if len(weibos) == 0:
			break
		#text ,
		#	origtext 
		#	count : bei zhuan ci shu,
		#	mcount : dianping times
		for m in weibos:
			all_weibos.append(m['text']+'!!!@#'+m['origtext']+'##!@#'+str(m['count'])+'$$!@#'+str(m['mcount']))
		if hasnext == 0: #has other contents
			last_id = weibos[-1]['id']
			last_page_time = weibos[-1]['timestamp']
		else:
			break
				
	return all_weibos

for user_name in users_dict.keys():
	for friend_name in users_dict[user_name]:
		print 'process user:' + friend_name
		if not os.path.exists('contents/' + friend_name):
			a = open('contents/' + friend_name, 'w')
			webos = get_weibo_of(friend_name)
			for i in webos:
				a.write(i+'\n')
			a.close()



