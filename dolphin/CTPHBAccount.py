#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pzyctp.stock import trader
import time
from conf.access_conf import access_conf

class CTPHBAccount():
    def __init__(self):
        self.trader = trader.Trader(access_conf['trader']['addr'], access_conf['trader']['broker'], access_conf['trader']['account'], access_conf['trader']['passwd'])
        time.sleep(5)
        self.stocklist = {}
        self.account_info= {}
        self.today_trades = []

    def buy(self, stockid, buy_infos):
        n_total_buy_num = 0
        n_total_buy_money = 0.0
        for (buy_price, buy_amount) in buy_infos:
            n_total_buy_num += buy_amount
            n_total_buy_money += buy_price * buy_amount
        if n_total_buy_num == 0:
            print 'None buy'
            return 0, 0

        n_total_buy_num = int(n_total_buy_num)
        buyprice = round(n_total_buy_money / n_total_buy_num, 2)
        self.trader.buy(stockid, str(buyprice+0.05), n_total_buy_num)
        
        return buyprice, n_total_buy_num

    def sell(self, stockid, sell_infos):
        n_total_sell_num = 0
        n_total_sell_money = 0.0
        for (sell_price, sell_amount) in sell_infos:
            n_total_sell_num += sell_amount
            n_total_sell_money += sell_price * sell_amount
        if n_total_sell_num == 0:
            print 'None sell'
            return 0, 0

        sellprice = round(n_total_sell_money / n_total_sell_num, 2)
        self.trader.sell(stockid, str(sellprice-0.05), n_total_sell_num)

        return sellprice, n_total_sell_num

    ''' 
        Account detailed info:
        ///资金差额
        TZQThostFtdcMoneyType   CashIn;
        ///手续费
        TZQThostFtdcMoneyType   Commission;
        ///融券持仓盈亏
        TZQThostFtdcMoneyType   CloseProfit;
        ///融资持仓盈亏
        TZQThostFtdcMoneyType   PositionProfit;
        ///期货结算准备金
        TZQThostFtdcMoneyType   Balance;
        ///现金
        TZQThostFtdcMoneyType   Available;
        ///可取资金
        TZQThostFtdcMoneyType   WithdrawQuota;
        ///基本准备金
        TZQThostFtdcMoneyType   Reserve;
    '''
    def get_account_info(self):
        return {'stocklist': self.stocklist, 'account': self.account_info}

    def update_account_info(self):
        self.trader.update_position_info()
        time.sleep(5)
        self.stocklist = self.trader.get_position_info()
        self.trader.update_account_info()
        time.sleep(5)
        self.account_info = self.trader.get_account_info()
        return

    def get_today_trades(self):
        return self.today_trades

    def update_today_trades(self):
        self.trader.update_trade_records()
        time.sleep(5)
        today_trades = self.trader.get_trade_records()
        combined_trades = []
        for trade in today_trades:
            record = trade.split()
            record[4] = float(record[4])
            record[5] = int(record[5])
            if_inserted = False
            for combined_trade in combined_trades:
                if record[3] == combined_trade[3] and record[2] == combined_trade[2]:
                    amount = record[5] + combined_trade[5]
                    if amount == 0:
                        break;
                    price = (record[4]*record[5] + combined_trade[4]*combined_trade[5]) / amount
                    combined_trade[4] = price
                    combined_trade[5] = amount
                    if_inserted = True
            if not if_inserted:
                combined_trades.append(record)

        combined_trades = [ self.correct_trade_format(trade) for trade in combined_trades ]

        self.today_trades = combined_trades

    def correct_trade_format(self, trade_record):
        TradeDate = trade_record[0]
        TradeDate = TradeDate[:4] + '-' + TradeDate[4:6] + '-' + TradeDate[6:]
        TradeDate += (' ' + trade_record[1])
        trade_record[0] = TradeDate
        trade_record.pop(1)
        trade_record.append('1')
        return trade_record

    def takeout_fund(self, amount):
        self.trader.takeout_fund(amount)




