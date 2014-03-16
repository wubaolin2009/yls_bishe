# simple use
from qqweibo import OAuthHandler, API, JSONParser, ModelParser
from qqweibo.utils import timestamp_to_str
import urllib, urllib2, http_helper

a = OAuthHandler('801486043', 'cd0a763d5f7d8be4f588b0f6f290fb06')
a = OAuthHandler('801486692', '35499dde285b599841fcee05aee4e28b')
a = OAuthHandler('801486694','122efd9274999d8eb06b185501611ca0')
aaaaa = OAuthHandler('801486696','c45b2b1afb0eae1e64466f7c9fd36319')
aaaaa = OAuthHandler('801486704','f8a0cb0327d53a71aba609707c3ea239')
aaaaa = OAuthHandler('801486706','ccb88ca0bd2d2ab59465abf45818567e')

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

#me = api.user.info()
#print me.name, me.nick, me.location


#nba = api.user.userinfo('NBA')

# 1. fetch the social network, starting from me, 
# Deep first search
start = '''rhhgjkli''' 
#fetch the user
def get_all_friends_of(user_name, at_most = 300):
	all_friends = set()
	for i in range( (at_most + 29 )// 30 ):
		try:
			lists = api.friends.userfanslist(requnum=30, startindex=i * 30, name=user_name)
			map(all_friends.add, [(m.name,m.nick) for m in lists])
			if len(lists) < 30:
				return all_friends
		except Exception, e:
			pass
				
	return all_friends


import pickle
from Queue import Queue

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

final_f = open('relations_new', 'a')
def fetch_friends(start, max = 10000):
	q = Queue()
	q.put(start)
	count = 0
	while not q.empty():
		user = q.get()
		count = count + 1
		if count % 10 == 0:
			final_f.flush()
		if count > max:
			return
		print 'processing user:', user
		if user not in users_dict.keys():
			users_dict[user] = []
			all_that = get_all_friends_of(user)
			print 'Got number of friends:' + str(len(all_that))
			for one_friend in all_that:
				friend_user, nick = one_friend
				if len(friend_user) == 0:
					print 'len_frien_user is 0'
					continue
				users_dict[user].append(friend_user)
				nicks[friend_user] = nick
				my_nick = nicks[user] if user in nicks.keys() else 'NoNo'
				print user,',',my_nick,'::::',friend_user,',',nick
				final_f.write((user+','+my_nick+'::::'+friend_user + ','+nick + '\n').encode('utf-8'))
		else:
			print 'already exists!'
		next = users_dict[user]
		for m in next:
			q.put(m)

fetch_friends(start)
#print users_dict
final_f.close()


#for t in me.timeline(reqnum=3):  # my timeline
        #print t.nick, t.text, timestamp_to_str(t.timestamp)

#nba = api.user.userinfo('NBA')
#for u in nba.followers(reqnum=3):  # get NBA's fans
        #u.follow()
        #break  # follow only 1 fans ;)
#u.unfollow()  # then unfollow

#for t in nba.timeline(reqnum=1):
        #print t.text
        #t.favorite()  # i like this very much

#for fav in api.fav.listtweet():
        #if fav.id == t.id:
                #fav.unfavorite()
