#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import fileinput

pair_array = []
value_array = []

for line in fileinput.input():
    item = line.strip().split()
    pair_array.append( item[0] )
    value_array.append( float(item[1]) )

value_array = numpy.array( value_array )
mean = value_array.mean()
std = value_array.std()
value_nor_array = (value_array-mean)/std

for i in range(0, len(pair_array)):
    print '\t'.join([ pair_array[i], str(value_nor_array[i])])

