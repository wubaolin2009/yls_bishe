# -*- coding: utf-8 -*-
# Convert 111 abc to 'abc' for the final use

FILE_NAME='wbl_80'
f = open(FILE_NAME, 'r')
f_out = open(FILE_NAME + '_converted', 'w')
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
	f_out.write((word+u'\r\n').encode('utf-8'))
f_out.close()