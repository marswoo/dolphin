#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fileinput
from time import *
import sys
import os

if len(sys.argv) != 3:
    print 'usage: python addTimeToData.py stock1 stock2'
    sys.exit(-1)

pair = (sys.argv[1], sys.argv[2])

rawdata_dir = './history_minutes_data/rawdata'
output_dir = './history_minutes_data'

for stock in pair:
    start_date = ""
    open_time = 0
    half_close_time = 0
    half_open_time = 0
    close_time = 0
    base_time = open_time
    first_line = True
    first_day = True
    minutes_from_openmarket = 0
    yesterday_close_price = '0'
    f1 = open(os.path.join(rawdata_dir, stock[0:]+'.txt'))
    f2 = open(os.path.join(output_dir, stock), 'w')
    for line in f1:
        items = line.strip().replace('\t\t', '\t').split('\t')
        if items[0] != start_date:
            if not first_day and minutes_from_openmarket < 121:
                f2.write( '\t'.join( [start_date+'_15:00:00'] + items[1:5] + [yesterday_close_price] ) + '\n' )
            if not first_day and minutes_from_openmarket < 120:
                print stock, start_date, 'Data Error, not enough lines'
            first_line = True
            minutes_from_openmarket = 0
        if first_line:
            start_date = items[0]
            open_time = mktime(strptime(start_date+' 09:30:00', '%Y-%m-%d %H:%M:%S'))
            half_close_time = mktime(strptime(start_date+' 11:30:00', '%Y-%m-%d %H:%M:%S'))
            half_open_time = mktime(strptime(start_date+' 13:00:00', '%Y-%m-%d %H:%M:%S'))
            close_time = mktime(strptime(start_date+' 14:59:00', '%Y-%m-%d %H:%M:%S'))
            first_line = False
            base_time = open_time
            if first_day:
                yesterday_close_price = items[1]
                first_day = False
        now_time = base_time + minutes_from_openmarket*60
        minutes_from_openmarket += 1

        items[0] = strftime('%Y-%m-%d_%H:%M:%S', localtime(now_time))
        items = items[:5]
        items.append(yesterday_close_price)
        f2.write('\t'.join(items) + '\n')

        if now_time == half_close_time:
            base_time = half_open_time
            minutes_from_openmarket = 0
        elif now_time >= close_time:
#            first_line = True
#            minutes_from_openmarket = 0
            yesterday_close_price = items[4]

    f1.close()
    f2.close()


''' join the pair files based on time '''
command = 'join ' + os.path.join(output_dir, pair[0]) + ' ' + os.path.join(output_dir, pair[1]) + ' >tmp'
os.system(command)

''' split the joined file to two stock files '''
f1 = open(os.path.join(output_dir, pair[0]), 'w')
f2 = open(os.path.join(output_dir, pair[1]), 'w')
with open('tmp') as ff:
    for line in ff:
        items = line.strip().split()
        items[0] = items[0].replace('_', '\t')
        f1.write( '\t'.join(items[:6]) + '\n' )
        f2.write( '\t'.join( [items[0]] + items[6:] ) + '\n' )

f1.close()
f2.close()




