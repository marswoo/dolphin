#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datafeeder, trader

def test_datafeeder():
    #测试账户
    #t = datafeeder.DataFeeder('tcp://211.144.195.163:44513', '2011', '020090042332', '123321')
    #t = datafeeder.DataFeeder('tcp://101.231.210.1:8900', '2011', '050000006268', '2111519')
    time.sleep(1)
    #t.subscrib_market_data('sz002029')
    t.subscrib_market_data('sz000157')
    while True:
        #print t.get_market_data('sz002029')
        print t.get_market_data('sz000157')
        time.sleep(2)

def test_trade():
    #测试账号
    t = trader.Trader('tcp://211.144.195.163:44505', '2011', '020090042332', '123321') 
    #time.sleep(2) #必须sleep，否则大不到账户信息

    #真实账号
    #t = trader.Trader('tcp://101.231.210.1:24505', '2011', '050000006268', '2111519')
    #t = trader.Trader('tcp://222.66.55.171:24505', '2011', '050000006071', '9163212')#hecor
    time.sleep(2) #必须sleep，否则大不到账户信息

    t.update_account_info() #获得账户里面的所有信息
    time.sleep(1) ##必须sleep，否则不能更新

    print "get_account_info"
    print t.get_account_info()
    print "get_position_info"
    print t.get_position_info()
    exit(0)
    print "sell"
    t.sell('sh600031', '2.0', 240) #GC
    time.sleep(2)

    print "buy"
    t.buy('sz002029', '20', 100)
    time.sleep(2)

    print "sell"
    t.sell('sz002029', '200', 100)
    time.sleep(2)

    #t.sell('sz002029', '20', 100)
    #time.sleep(2) ##必须sleep，否则不能更新

    t.update_account_info() #获得账户里面的所有信息
    time.sleep(2)

    print "get_account_info"
    print t.get_account_info()
    #t.buy('sh601566', '8.9', 100)
    #t.sell('sh204007', '11.90', 100)
    #t.update_stock_info()
    #time.sleep(3)
    #print t.get_stock_info()

    #t.update_trade_records()
    #time.sleep(3)
    #print t.get_trade_records()

    #t.takeout_fund(10000)
    #time.sleep(5)

if __name__ == '__main__':
    test_datafeeder()
    #test_trade()
    time.sleep(1)
