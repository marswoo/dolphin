#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fileinput

for line in fileinput.input():
    item = line.strip().split()
    final_score = 0.425*float(item[1]) + 0.425*float(item[2]) + 0.15*float(item[3])
    print '\t'.join(item + [str(final_score)])

