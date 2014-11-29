#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pzyctp.stock import datafeeder
import time

class CTPL2StockDataFeeder:
    def __init__(self):
        self.l2data = datafeeder.DataFeeder('tcp://101.231.210.1:24513', '2011', '050000006268', '2111519')
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

