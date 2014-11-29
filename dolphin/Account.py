#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime, urllib2

class Account:
    def sell(self, stockid, buy_infos):
        raise NotImplementedError( "Should have implemented this" )

    def buy(self, stockid, sell_infos):
        raise NotImplementedError( "Should have implemented this" )

    def get_account_info(self):
        raise NotImplementedError( "Should have implemented this" )
    
    def update_account_info(self):
        raise NotImplementedError( "Should have implemented this" )

    def get_today_trades(self):
        raise NotImplementedError( "Should have implemented this" )


class VirtualAccount(Account):
    def __init__(self):
        self.cash = 1000000;
        self.stocklist = {}
    
    def buy(self, stockid, buy_infos):
        n_total_buy_num = 0
        n_total_buy_money = 0.0
        for (buy_price, buy_amount) in buy_infos:
            n_total_buy_num += buy_amount
            n_total_buy_money += buy_price * buy_amount
        if n_total_buy_num <= 0:
            return 0, 0
        if n_total_buy_money <= self.cash:
            self.cash -= n_total_buy_money
            # 交易成本
            self.cash -= max(n_total_buy_money*0.0006, 5)
            if stockid.startswith('sh'):
                self.cash -= n_total_buy_num * 0.01 * 0.06

            if stockid in self.stocklist.keys():
                self.stocklist[stockid] = self.stocklist[stockid] + n_total_buy_num
            else:
                self.stocklist[stockid] = n_total_buy_num
            n_total_buy_price = n_total_buy_money / n_total_buy_num
        else:
            raise Exception("Not enough cash")

        return n_total_buy_price, n_total_buy_num


    ''' 支持卖空 '''
    def sell(self, stockid, sell_infos):
        if stockid not in self.stocklist.keys():
            self.stocklist[stockid] = 0
        n_total_sell_num = 0
        n_total_sell_money = 0.0
        for (sell_price, sell_amount) in sell_infos:
            n_total_sell_num += sell_amount
            n_total_sell_money += sell_price * sell_amount
        if n_total_sell_num <= 0:
            return 0, 0
#        if self.stocklist[stockid] < n_total_sell_num:
#            raise Exception("Not enough stock for " + stockid)
        self.stocklist[stockid] -= n_total_sell_num
        self.cash += n_total_sell_money
        # 交易成本
        self.cash -= max(n_total_sell_money*0.0006, 5)
        self.cash -= n_total_sell_money*0.001
        if stockid.startswith('sh'):
            self.cash -= n_total_sell_num * 0.01 * 0.06

        n_total_sell_price = n_total_sell_money / n_total_sell_num
        return n_total_sell_price, n_total_sell_num

    def get_account_info(self):
        return {'cash':self.cash, 'stocklist':self.stocklist}
    
    def update_account_info(self):
        return

    def get_today_trades(self):
        return []


class LocalWebServiceAccount(Account):
    def __init__(self):
        self.base_url = 'http://127.0.0.1:8082/dolphin/trade/'

    def update_account_info(self):
        content = urllib2.urlopen(self.base_url+'update_account_info/').read()
        return

    def get_account_info(self):
        content = urllib2.urlopen(self.base_url+'get_account_info/').read()
        return eval(content)

    def get_today_trades(self):
        content = urllib2.urlopen(self.base_url+'get_today_trades/').read()
        return eval(content)

    def buy(self, stockid, buy_infos):
        n_total_buy_num = 0
        n_total_buy_money = 0.0
        for (buy_price, buy_amount) in buy_infos:
            n_total_buy_num += buy_amount
            n_total_buy_money += buy_price * buy_amount
        if n_total_buy_num == 0:
            return 0, 0

        n_total_buy_num = int(n_total_buy_num)
        buyprice = round(n_total_buy_money / n_total_buy_num, 2)
        urllib2.urlopen(self.base_url+'buy_'+stockid+'_'+str(buyprice)+'_'+str(n_total_buy_num)+'/')
        return buyprice, n_total_buy_num

    def sell(self, stockid, sell_infos):
        n_total_sell_num = 0
        n_total_sell_money = 0.0
        for (sell_price, sell_amount) in sell_infos:
            n_total_sell_num += sell_amount
            n_total_sell_money += sell_price * sell_amount
        if n_total_sell_num == 0:
            return 0, 0

        n_total_sell_num = int(n_total_sell_num)
        sellprice = round(n_total_sell_money / n_total_sell_num, 2)
        urllib2.urlopen(self.base_url+'sell_'+stockid+'_'+str(sellprice)+'_'+str(n_total_sell_num)+'/')
        return sellprice, n_total_sell_num


if __name__ == "__main__":
    op = LocalWebServiceAccount()
#    op.buy(stockid, [(1.2, 200)])
#    op.sell(stockid, [(1.2, 100)])
    print op.get_account_info()
    print op.get_today_trades()

