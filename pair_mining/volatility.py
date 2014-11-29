#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

data_dir = sys.argv[1]
START_DATE = sys.argv[2]

for file in os.listdir(data_dir):
    stockid = file[:6]
    volatility = 0.0
    with open(os.path.join(data_dir+file)) as f:
        items = [ item.split('\t') for item in f.read().split('\n')[:-1] ]
        items = [ float(item[2]) for item in items if item[0].replace('/', '') >= START_DATE ]
        if len(items) == 0:
            volatility = 0
        else:
            volatility = sum(items) / len(items)
    print stockid, volatility


