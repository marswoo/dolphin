#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fileinput

stock_volatility = {}
with open('volatility.dat') as f:
    for line in f:
        items = line.strip().split()
        stock_volatility[items[0]] = items[1]

for line in fileinput.input():
    pairid = line.split()[0]
    pair = pairid.split('VS')
    print pairid + '\t' + str(max(stock_volatility[pair[0]], stock_volatility[pair[1]]))

