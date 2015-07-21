#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

dirs = ['/tmp/CTP_LTS_trade/', '/tmp/CTP_LTS_data/']
for d in dirs:
    if not os.path.isdir(d):
        os.makedirs(d)

