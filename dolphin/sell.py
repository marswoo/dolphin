#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from Account import LocalWebServiceAccount
import sys

if __name__ == '__main__':
    stock_code = sys.argv[1]
    price = float(sys.argv[2])
    amount = int(sys.argv[3])
    print "sell info:"
    print '{0:10s}{1:<20s}\n{2:10s}{3:<10.6f}\n{4:10s}{5:<10d}'.format("stockid: ", stock_code, "price: ", price, "amount: ", amount)
    
    trader = LocalWebServiceAccount()

    trader.update_account_info()
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
        exit(1)
    

    print trader.sell(stock_code, [(price, amount)])

    trader.update_account_info()
    print 'Today deals:'
    deals = trader.get_today_trades()
    for i in deals:
        print i
