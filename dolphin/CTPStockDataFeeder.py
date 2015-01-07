#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pzyctp.stock import datafeeder
import time
from conf.access_conf import access_conf

class CTPL2StockDataFeeder:
    def __init__(self):
        self.l2data = datafeeder.DataFeeder(access_conf['datafeeder']['addr'], access_conf['datafeeder']['broker'], access_conf['datafeeder']['account'], access_conf['datafeeder']['passwd'])
        self.ExchangeIDDict = {'sh': 'SSE', 'sz': 'SZE'}
        self.ExchangeIDDict_reverse = {'SSE': 'sh', 'SZE': 'sz'}
        time.sleep(5)

    def subscribe(self, stockid):
        #self.l2data.subscrib_L2_market_data(stockid)
        self.l2data.subscrib_market_data(stockid)

    def get_data(self, stockid):
        #return self.l2data.get_L2_market_data(stockid)
        return self.l2data.get_market_data(stockid)

    
if __name__ == "__main__":
    import time
    feeder = CTPL2StockDataFeeder()
    feeder.subscribe('sz002029')
    while True:
        print feeder.get_data('sz002029')
#        data2 = feeder.get_data('sh601566')
        time.sleep(2)

