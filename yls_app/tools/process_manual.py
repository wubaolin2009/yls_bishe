# -*- coding: utf-8 -*-
# This file is used to converted manually marked vocabulary
# to a web server readable format
import os

a = open('/home/wubaolin/wbl_80_converted', 'r')
out = open('/home/wubaolin/wbl_80_converted_manual_processed','w')
for m in a.readlines():
    l = m.decode('utf-8')
    l = l.replace(u'\r', u'')
    l = l.replace(u'\n', u'')
    if u'/' in l and u'//' not in l:
        continue
    l = l.replace(u'/',u'')
    out.write((l+u'\n').encode('utf-8'))

out.close()
