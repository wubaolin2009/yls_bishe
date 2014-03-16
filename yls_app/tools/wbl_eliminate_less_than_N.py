# -*- coding: utf-8 -*-
FILE_NAME=r'C:\contents\tools\wbl'

import os
N = 80

count = 0
def incr_count():
	global count
	count += 1
	if count % 1000 == 0:
		print count

out_list = []

def func_cmp(a,b):
	a1 = int(a[0])
	b1 = int(b[0])
	return a1 - b1

f = open(FILE_NAME, 'r')
f_out = open(FILE_NAME + '_' + str(N), 'w')
for l in f.readlines():
	l = l.decode('utf-8').replace(u'\n', u'')
	r = l.split(u' ')
	times = 0
	for i in range(len(r)):
		if r[i].isdigit():
			times = r[i]
			continue
		if times != 0:
			word = r[i]
			break
	if int(times) > N and len(word) > 1:
		out_list.append( (times,word) )
		incr_count
		

out_list.sort(reverse=True, cmp=func_cmp)
for o in out_list:
	times, word = o
	f_out.write((times + u' ' + word + u'\n').encode('utf-8'))

f_out.close()
f.close()

