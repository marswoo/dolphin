#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fileinput
from heapq import *
from collections import defaultdict

stock_areas = defaultdict(list)
stock_name = {}
with open('stocklist.txt') as f:
    for line in f:
        item = line.strip().split('\t')
        if len(item) != 3:
            print 'error:', line
            continue
        stock_areas[item[0][2:]].append(item[2])
        stock_name[item[0][2:]] = item[1]


top_pair = {}
top_count = 10

for line in fileinput.input():
    item = line.strip().split()
    pair = item[0].split('VS')

    common_area = None
    for a1 in stock_areas[pair[0]]:
        for a2 in stock_areas[pair[1]]:
            if a1 == a2:
                common_area = a1
                break
        if common_area:
            break

    if common_area:
        new_pair = [ pair[0]+'/'+stock_name[pair[0]], pair[1]+'/'+stock_name[pair[1]] ]
        new_pair = item[1:] + new_pair
        final_score = float(item[4])

        if common_area not in top_pair.keys():
            top_pair[common_area]  = []
        if len(top_pair[common_area]) < top_count:
            heappush(top_pair[common_area], (final_score, new_pair))
        elif final_score > min([ i[0] for i in top_pair[common_area] ]):
            heapreplace(top_pair[common_area], (final_score, new_pair))
            

for key, value in top_pair.iteritems():
    print key
    for v in value:
        print '\t'.join(v[1])
    print '\n'


