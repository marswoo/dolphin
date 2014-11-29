#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
from lxml import etree
import math

total_hit = 1000000000

def get_hit(query):
    url = 'http://www.baidu.com/s?rsv_spt=1&issp=1&rsv_bp=0&ie=utf-8&tn=baiduhome_pg&rsv_n=2&rsv_sug3=13&rsv_sug1=4&rsv_sug4=37321&rsv_sug=1&inputT=11585&wd='+query
    response = urllib2.urlopen(url)

    htmlparser = etree.HTMLParser()
    tree = etree.parse(response, htmlparser)
    elem = tree.xpath('//*[@id="page"]/span')[0]
    hit = elem.text[ elem.text.find(u'相关结果约')+len(u'相关结果约') : elem.text.find(u'个') ]
    hit = long(hit.replace(',', ''))

    return hit

def google_distance( word1, word2 ):
    f1 = get_hit(word1)
    f2 = get_hit(word2)
    f12 = get_hit( word1 + '%20' + word2 )
    sim = max(math.log(f1, 2), math.log(f2, 2)) - math.log(f12, 2)
    sim /= math.log(total_hit, 2) - min(math.log(f1, 2), math.log(f2, 2))

    return sim

if __name__ == '__main__':
    import sys
    print google_distance(sys.argv[1], sys.argv[2])
#    print '新和成_浙江医药', google_distance('新和成', '浙江医药')
#    print '中联重科_三一重工', google_distance('中联重科', '三一重工')

#    stock_list = {}
#    with open('stocklist.txt') as f:
#        for line in f:
#            item = line.strip().split('\t')
#            stock_list[item[0][2:]] = item[1]
#    
#    pair_list = []
#    with open('tmp') as f:
#        for line in f:
#            try:
#                item = line.strip().split('VS')
#                pair_list.append( (line.strip(), stock_list[item[0]], stock_list[item[1]]) )
#            except KeyError:
#                pass
#
#    import time
#    with open('google_distance.dat', 'a') as f:
#        for pair in pair_list:
#            print pair[1], pair[2]
#            f.write(pair[0] + '\t' + str(google_distance(pair[1], pair[2])) + '\n')
#            f.flush()



