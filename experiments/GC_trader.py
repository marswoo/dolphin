#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from Account import LocalWebServiceAccount

if __name__ == '__main__':
    trader = LocalWebServiceAccount()
    
    trader.update_account_info()
    available_mount = int(trader.get_account_info()['account']['Available']/1000)
    print available_mount

    # 10 -> 1000Yuan
    trader.sell('sz131810', [(2.0, available_mount*10)])

    print 'Today deals:', trader.get_today_trades()
    time.sleep(10)

