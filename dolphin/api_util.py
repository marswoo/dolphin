#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from api import datafeeder, trader
#from pzyctp.stock import datafeeder, trader
from conf.access_conf import access_conf

def get_stock_data(stock_id, t_datafeeder):
    t_datafeeder.subscrib_market_data(stock_id)
    time.sleep(1)
    return t_datafeeder.get_market_data(stock_id)

def buy(stock_id, price, amount, t_trader):
    t_trader.update_account_info() #获得账户里面的所有信息
    time.sleep(1) ##必须sleep，否则不能更新
    t_trader.buy(str(stock_id), str(price), int(amount))
    time.sleep(1)

def sell(stock_id, price, amount, t_trader):
    t_trader.update_account_info() #获得账户里面的所有信息
    time.sleep(1) ##必须sleep，否则不能更新
    t_trader.sell(str(stock_id), str(price), int(amount))
    time.sleep(1)

def get_account_info(t_trader):
    print "get_account_info"
    t_trader.update_account_info()
    time.sleep(2)
    return t_trader.get_account_info()

def get_position_info(t_trader):
    print "get_position_info"
    t_trader.update_position_info()
    time.sleep(2)
    return t_trader.get_position_info()

def get_trader():
    t_trader = trader.Trader(access_conf['trader']['addr'], access_conf['trader']['broker'], access_conf['trader']['account'], access_conf['trader']['passwd'])
    time.sleep(2)
    return t_trader

def get_datafeeder():
    t_datafeeder = datafeeder.DataFeeder(access_conf['datafeeder']['addr'], access_conf['datafeeder']['broker'], access_conf['datafeeder']['account'], access_conf['datafeeder']['passwd'])
    time.sleep(2)
    return t_datafeeder

if __name__ == '__main__':
    #print get_stock_data("sz000157", get_datafeeder())
    #print get_account_info(get_trader())
    print get_position_info(get_trader())
    #sell("sz002474", 12.20, 1500, get_trader())
    time.sleep(1)
