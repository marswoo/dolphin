#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from pzyctp.stock_ctp import datafeeder, trader

def test_datafeeder():
    t = datafeeder.DataFeeder('tcp://180.166.11.40:41213', '2011', '20000479', '154097')
    time.sleep(1)
    t.subscrib_market_data('sz002029')
    while True:
        print t.get_market_data('sz002029')
        time.sleep(2)

def test_trade():
    t = trader.Trader('tcp://180.166.11.40:41205', '2011', '20000479', '154097')
    t.update_account_info()
    time.sleep(1)
    print t.get_account_info()
    t.buy('sz002029', '20', 100)
    time.sleep(5)

if __name__ == '__main__':
    #test_datafeeder()
    test_trade()

