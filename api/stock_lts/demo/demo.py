#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from pzyctp.stock import datafeeder, trader

def test_datafeeder():
    #t = datafeeder.DataFeeder('tcp://211.144.195.163:44513', '2011', '020090042332', '123321')
    t = datafeeder.DataFeeder('tcp://101.231.210.1:24513', '2011', '050000006268', '2111519')
    #t = datafeeder.DataFeeder('tcp://101.231.210.1:8900', '2011', '050000006268', '2111519')
    time.sleep(1)
    t.subscrib_market_data('sz002029')
    while True:
        print t.get_market_data('sz002029')
        time.sleep(2)

def test_trade():
    t = trader.Trader('tcp://211.144.195.163:44505', '2011', '020090042332', '123321')
    #t = trader.Trader('tcp://101.231.210.1:24505', '2011', '050000006268', '2111519')
    t.update_account_info()
    time.sleep(1)
    print t.get_account_info()
    #t.buy('sz002029', '20', 100)
    #t.buy('sh601566', '8.9', 100)
#    t.sell('sh204007', '11.90', 100)

#    t.update_stock_info()
#    time.sleep(3)
#    print t.get_stock_info()
#
#    t.update_trade_records()
#    time.sleep(3)
#    print t.get_trade_records()
#
#    t.takeout_fund(10000)
#    time.sleep(5)

if __name__ == '__main__':
    #test_datafeeder()
    test_trade()

    time.sleep(5)
