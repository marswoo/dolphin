#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from Account import LocalWebServiceAccount

if __name__ == '__main__':
    trader = LocalWebServiceAccount()

    trader.update_account_info()
    '''
    account:
    {'account': {'Available': 504.08739999999875, 'Commission': 19.390599999999999, 'WithdrawQuota': 504.08739999999875, 'Credit': 0.0, 'Balance': 504.08739999999875, 'Reserve': 0.0}, 'stocklist': {'sz002279': 600, 'sz000858': 0, 'sz000561': 0, 'sz131810': 0}}
    Today deals:
    [['2014-12-05 09:30:09', '0', 'sz000561', 9.9299999999999997, 2000, '1'], ['2014-12-05 09:31:13', '1', 'sz002279', 34.936666666666667, 600, '1'], ['2014-12-05 09:31:29', '0', 'sz000858', 20.48, 1000, '1'], ['2014-12-05 13:15:10', '0', 'sz131810', 100.0, 100, '1'], ['2014-12-05 20:14:12', '1', 'sz131810', 3.8500000000000001, 0, '1'], ['2014-12-05 20:14:12', '1', 'sz131810', 3.8500000000000001, 0, '1']]
    '''
    acc = trader.get_account_info()
    if acc:
        print "account:"
        if len(acc["account"]) != 0:
            for key in acc["account"]:
                print "{0:20s}:{1:.5}".format(key, float(acc["account"][key]))
        else:
            print acc
    else:
        print "account empty."

    print
    

    #available_mount = int(trader.get_account_info()['account']['Available']/1000)
    #print "available_mount:"
    #print available_mount

    ## 10 -> 1000Yuan
    #print "sell"
    #print trader.sell('sz131810', [(2.0, available_mount*10)])
    #trader.buy('sz131810', [(2.0, available_mount*10)])

    trader.update_account_info()
    print 'Today deals:'
    deals = trader.get_today_trades()
    for i in deals:
        print i
    #time.sleep(10)
