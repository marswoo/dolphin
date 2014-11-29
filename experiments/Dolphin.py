#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Util import *
import math, time, datetime


class Dolphin(object):
    def __init__(self, pairid, data_feeder, account):
        self.pairid = pairid
        items = pairid.split('_')
        self.stockid_1 = items[0]
        self.stockid_2 = items[1]
        self.stockdata_1 = {}
        self.stockdata_2 = {}
        self.expense_each_deal = 20000.0
        self.max_profit = 0.03
        self.continuous_delta_count = 1
        self.stoploss_minutes_to_closemarket = 3
        self.data_feeder = data_feeder
        self.account = account
        self.pair_setting = get_pairsetting( pairid )
        self.base_enter_threshold = self.pair_setting['base_enter_threshold']

        self.account.update_account_info()
        time.sleep(5)
        log('debug_info', self.account.get_account_info())

        self.new_day()


    def close_today(self):
#        if if_need_update_real_deal(self.pairid):
        today_trades = self.account.get_today_trades()
        for trade in today_trades:
            if trade[2] in (self.stockid_1, self.stockid_2):
                log('realdeal_info', '\t'.join([str(item) for item in trade]))
        update_asset(self.pairid, self.today_date, self.get_virtual_profit() )

        self.pair_setting['max_delta_of_yesterday'] = self.max_delta_of_today
        self.pair_setting['base_enter_threshold_yesterday'] = self.base_enter_threshold
        update_pairsetting(self.pairid, self.pair_setting)


    def new_day(self):
        self.today_date = str(datetime.date.today())
        ''' 0: haven't done any deal this day; 
            1: already bought stock id1; 
            2: already bought stock id2; 
            3: already done deal today, only read data;
        '''
        self.today_bought_stock = 0
        self.today_bought_amount = { self.stockid_1:0, self.stockid_2:0 }
        
        self.calculate_new_base_threshold()
        log('threshold_info', '\t'.join([ 'Enter threshold', self.today_date, self.pairid, str(self.pair_setting['base_enter_threshold']), str(self.pair_setting['max_delta_of_yesterday']), str(self.base_enter_threshold) ]))

        self.delta_relative_price_when_entering_market = -100
        self.delta_relative_price_when_leaving_market = -100
        self.if_enter_triggered = False
        self.max_delta_of_today = 0
        self.minutes_to_closemarket = 240
         
        self.account.update_account_info()


    '''
        动态调整每天的入场阈值：根据前一天的阈值和delta最大值
    '''
    def calculate_new_base_threshold(self):
        max_delta_of_yesterday = self.pair_setting['max_delta_of_yesterday']
        if max_delta_of_yesterday <= 0:
            return
        self.base_enter_threshold = self.pair_setting['base_enter_threshold_yesterday']
        #xi = max_delta_of_yesterday - self.base_enter_threshold - 0.005
        xi = max_delta_of_yesterday - self.base_enter_threshold - pow((self.base_enter_threshold / 0.015), 0.5) * 0.005
        if xi >= 0:
            #yi = (math.pow(1 + abs(xi*200), 0.4) - 1)/200;
            yi = min((math.pow(1 + abs(xi*200), 0.4) - 1)/200, 0.006);
            self.base_enter_threshold += yi
        else:
            yi = (math.pow(1 + abs(xi*200), 0.6) - 1)/200;
            self.base_enter_threshold -= yi

        self.base_enter_threshold = min(max(self.base_enter_threshold, 0.0125), 0.04)
        

    ''' 判断是否入场 '''
    def if_enter_market(self, continuous_deltas_rightnow, stock_index):
        return min(continuous_deltas_rightnow[stock_index]) >= self.get_delta_threshold_of_entering_market()


    '''
    距离收市分钟数x
    入市条件：
    '''
    def get_delta_threshold_of_entering_market(self):
        base = self.base_enter_threshold
        enter_threshold = [([240, 235], self.pair_setting['base_enter_threshold']-0.006), ([235, 210], base-0.004), ([210, 180], base-0.002), ([180, 120], base), ([120, 0], 100)]
        for threshold in enter_threshold:
            if self.minutes_to_closemarket > threshold[0][1] and self.minutes_to_closemarket <=  threshold[0][0]:
                return threshold[1]
         
        return 100


    '''
    获利了结映射表
    '''
    def get_delta_threshold_of_exiting_market(self):
        base = self.pair_setting['base_exit_threshold']
        exit_threshold = [([240, 210], base), ([210, 180], base+0.001), ([180, 150], base+0.002), ([150, 120], base+0.003), ([120, 90], base+0.006), ([90, 60], base+0.007), ([60, 30], base+0.008), ([30, 0], base+0.009)]
        for threshold in exit_threshold:
            if self.minutes_to_closemarket > threshold[0][1] and self.minutes_to_closemarket <= threshold[0][0]:
                return threshold[1]

        return 0

        
    '''
    止损映射表：
    入市时的delta + 1% (或者改成足够大的数，则根本不止损，等着情况变好，如果情况没变好则等着最后4分钟强制处理)
    '''
    def get_delta_threshold_of_stopping_loss(self):
        return math.fabs(self.delta_relative_price_when_entering_market) + 0.1


    ''' 
    获取实际交易买卖价格
    如果没用足够的量或涨停跌停：price返回-1，买卖信息为空
    '''
    def get_deal_price(self, stock_data):
        # buy deal price
        want_unit_amount = round(self.expense_each_deal / stock_data['current_price'] / 100)
        total_cost = 0.0
        already_buy_unit_amount = 0
        buy_infos = []
        for i in range(1, 4):
            has_unit_num = stock_data['sell_'+str(i)+'_amount'] / 100
            actual_buy_unit = min(has_unit_num, want_unit_amount-already_buy_unit_amount)
            already_buy_unit_amount += actual_buy_unit
            total_cost += actual_buy_unit * stock_data['sell_'+str(i)+'_price']
            buy_infos.append( (stock_data['sell_'+str(i)+'_price'], int(actual_buy_unit)*100) )
            if already_buy_unit_amount == want_unit_amount:
                break
            
        deal_buy_price = -1
        if already_buy_unit_amount == want_unit_amount:
            deal_buy_price = total_cost / already_buy_unit_amount

        # sell deal price
        stockinfos = self.account.get_account_info()['stocklist']
        already_own_unit_amount = 0
        if stock_data['id'] in stockinfos.keys():
            already_own_unit_amount = stockinfos[stock_data['id']] / 100
        if already_own_unit_amount != 0:
            want_unit_amount = already_own_unit_amount
        total_cost = 0.0
        already_sell_unit_amount = 0
        sell_infos = []
        for i in range(1, 4):
            has_unit_num = stock_data['buy_'+str(i)+'_amount'] / 100
            actual_sell_unit = min(has_unit_num, want_unit_amount-already_sell_unit_amount)
            already_sell_unit_amount += actual_sell_unit
            total_cost += actual_sell_unit * stock_data['buy_'+str(i)+'_price']
            sell_infos.append( (stock_data['buy_'+str(i)+'_price'], actual_sell_unit*100) )
            if already_sell_unit_amount == want_unit_amount:
                break
            
        deal_sell_price = -1
        if already_sell_unit_amount == want_unit_amount:
            deal_sell_price = total_cost / already_sell_unit_amount
        if already_own_unit_amount == 0:
            sell_infos = []

        return deal_buy_price, buy_infos, deal_sell_price, sell_infos


    def buy(self, stockid, buy_infos):
        buyprice, buynum = self.account.buy(stockid, buy_infos)
        self.today_bought_amount[stockid] = buynum
        if buynum > 0:
            log('buy_info', '\t'.join([ str(datetime.datetime.today()), '0', stockid, str(buyprice), str(buynum), '0' ]) )
        

    def sell(self, stockid, sell_infos):
        sellprice, sellnum = self.account.sell(stockid, sell_infos)
        if sellnum > 0:
            log('sell_info', '\t'.join([ str(datetime.datetime.today()), '1', stockid, str(sellprice), str(sellnum), '0' ]) )


    def log_stockdata(self, stockdata_1, stockdata_2):
        for stock_data in (stockdata_1, stockdata_2):
            record = '\t'.join([ 
                stock_data['id'],  self.today_date+' '+stock_data['time'], 
                str(stock_data['current_price']), 
                str(stock_data['yesterday_close_price']), str(stock_data['today_open_price']), 
                str(stock_data['today_highest_price']), str(stock_data['today_lowest_price']),
                str(stock_data['deal_stock_amount']), str(stock_data['deal_stock_money']),
                str(stock_data['buy_1_price']), str(stock_data['buy_1_amount']),
                str(stock_data['buy_2_price']), str(stock_data['buy_2_amount']),
                str(stock_data['buy_3_price']), str(stock_data['buy_3_amount']),
                str(stock_data['sell_1_price']), str(stock_data['sell_1_amount']),
                str(stock_data['sell_2_price']), str(stock_data['sell_2_amount']),
                str(stock_data['sell_3_price']), str(stock_data['sell_3_amount'])
            ])
            log('stock_realdata', record)

   
    ''' 平仓离场，卖掉今天已买的，买入今天卖出的 '''
    def leave_market(self, sell_stockid, sell_infos, buy_stockid, buy_infos, delta):
        self.sell(sell_stockid, sell_infos)
        self.buy(buy_stockid, buy_infos)
        self.today_bought_stock = -1
        self.delta_relative_price_when_leaving_market = delta


    ''' 计算今日收益 '''
    def get_virtual_profit(self):
        if self.delta_relative_price_when_entering_market == -100 or self.delta_relative_price_when_leaving_market == -100:
            return 0

        if self.delta_relative_price_when_leaving_market is None:
            return -2000

        return (self.delta_relative_price_when_entering_market + self.delta_relative_price_when_leaving_market - 0.0032) * self.expense_each_deal

    
    ''' get stock meta information '''    
    def get_stock_data(self):
        # 每隔2s获取一次数据
        time.sleep(2)

        # 计算得到当前时间，距离当天收市的时间，分钟表示
        now_time = strftime('%H:%M:%S', localtime())
        self.minutes_to_closemarket = get_minutes_to_closemarket(now_time)
        if self.minutes_to_closemarket < 0:
            self.close_today()
            return False
        elif self.minutes_to_closemarket == 120:
            self.data_feeder.wait_for_half_open()
            return True
        
        self.stockdata_1 = self.data_feeder.get_data(self.stockid_1)
        self.stockdata_2 = self.data_feeder.get_data(self.stockid_2)
            
#        if get_time_interval_seconds(now_time, stockdata_1['time']) > 30 or get_time_interval_seconds(stockdata_1['time'], stockdata_2['time']) > 30:
#            log('time_error', "time interval error between two stocks!" + stockdata_1['time'] + ':' + stockdata_2['time'] )
            
        return True

    
    ''' run dolphin to a pair of stocks '''
    def run(self):
        continuous_deltas_rightnow = [ 0, [0]*self.continuous_delta_count, [0]*self.continuous_delta_count ]
        while True:
            if not self.get_stock_data():
                return

            stockdata_1 = self.stockdata_1
            stockdata_2 = self.stockdata_2
            if stockdata_1 is None or stockdata_2 is None or stockdata_1['current_price'] == 0 or stockdata_2['current_price'] == 0:
                log('GetStockData_error', ' Get Stock data error!')
                continue
            else:
                self.log_stockdata( stockdata_1, stockdata_2 )
            
            current_buy_price_id_1, buy_infos_1, current_sell_price_id_1, sell_infos_1 = self.get_deal_price(stockdata_1)
            current_buy_price_id_2, buy_infos_2, current_sell_price_id_2, sell_infos_2  = self.get_deal_price(stockdata_2)

            ''' [0] not used; 
                [1] represents delta for buy 1, sell 2; 
                [2] represents delta for buy 2, sell 1;
            '''
            current_delta_relative_prices = [None]*3
            if current_buy_price_id_1 != -1 and current_sell_price_id_2 != -1:
                current_relative_price_id_1 = (current_buy_price_id_1 - stockdata_1['yesterday_close_price']) / stockdata_1['yesterday_close_price']
                current_relative_price_id_2 = (current_sell_price_id_2 - stockdata_2['yesterday_close_price']) / stockdata_2['yesterday_close_price']
                if math.fabs(current_relative_price_id_1) > 0.11 or math.fabs(current_relative_price_id_2) > 0.11:
                    log('delta_error', 'data overflow')
                    continue
                current_delta_relative_prices[1] = current_relative_price_id_2 - current_relative_price_id_1
            if current_sell_price_id_1 != -1 and current_buy_price_id_2 != -1:
                current_relative_price_id_1 = (current_sell_price_id_1 - stockdata_1['yesterday_close_price']) / stockdata_1['yesterday_close_price']
                current_relative_price_id_2 = (current_buy_price_id_2 - stockdata_2['yesterday_close_price']) / stockdata_2['yesterday_close_price']
                if math.fabs(current_relative_price_id_1) > 0.11 or math.fabs(current_relative_price_id_2) > 0.11:
                    log('delta_error', 'data overflow')
                    continue
                current_delta_relative_prices[2] = current_relative_price_id_1 - current_relative_price_id_2
        
            log('delta_info', '\t'.join([ self.pairid, self.today_date+' '+stockdata_1['time'], str(int(self.minutes_to_closemarket)), str(current_delta_relative_prices[1]), str(current_delta_relative_prices[2]) ]))
            
            for i in [1,2]:
                continuous_deltas_rightnow[i].pop(0)
                continuous_deltas_rightnow[i].append( current_delta_relative_prices[i] )
            
            self.max_delta_of_today = max(self.max_delta_of_today, current_delta_relative_prices[1], current_delta_relative_prices[2])

            # 当天尚未交易
            if self.today_bought_stock == 0:
                if self.if_enter_market(continuous_deltas_rightnow, 1):
                    log('deal_debug', 'delta差价足够大，达到给定阈值，建立头寸；' )
                    self.sell(self.stockid_2, sell_infos_2)
                    self.buy(self.stockid_1, buy_infos_1)
                    self.today_bought_stock = 1
                    self.delta_relative_price_when_entering_market = current_delta_relative_prices[1]
                elif self.if_enter_market(continuous_deltas_rightnow, 2):
                    log('deal_debug', 'delta差价足够大，达到给定阈值，建立头寸；' )
                    self.sell(self.stockid_1, sell_infos_1)
                    self.buy(self.stockid_2, buy_infos_2)
                    self.today_bought_stock = 2
                    self.delta_relative_price_when_entering_market = current_delta_relative_prices[2]

            #当天已经交易（已建立头寸）
            else:
                if self.today_bought_stock == 2:
                    if current_delta_relative_prices[1] is not None and (0-current_delta_relative_prices[1]) < self.get_delta_threshold_of_exiting_market():
                        log('deal_debug', 'delta差价缩小，回归正常值，对头寸进行获利了结；卖掉之前买入，买回之前卖出' )
                        self.leave_market(self.stockid_2, sell_infos_2, self.stockid_1, buy_infos_1, current_delta_relative_prices[1])
                        continue

                    if current_delta_relative_prices[1] is not None and (0-current_delta_relative_prices[1]) > self.get_delta_threshold_of_stopping_loss():
                        log('deal_debug', 'delta差价继续拉大，达到给定阈值，进行止损；卖掉之前买入，买回之前卖出；' )
                        self.leave_market(self.stockid_2, sell_infos_2, self.stockid_1, buy_infos_1, current_delta_relative_prices[1])
                        continue

                    if self.minutes_to_closemarket <= self.stoploss_minutes_to_closemarket:
                        log('deal_debug', 'delta差价没有缩小，距离今日收盘仅剩'+str(self.stoploss_minutes_to_closemarket)+'分钟，强制对头寸进行了结；卖掉之前买入，买回之前卖出；' )
                        self.leave_market(self.stockid_2, sell_infos_2, self.stockid_1, buy_infos_1, current_delta_relative_prices[1])
                        continue


                elif self.today_bought_stock == 1:
                    if current_delta_relative_prices[2] is not None and (0-current_delta_relative_prices[2]) < self.get_delta_threshold_of_exiting_market():
                        log('deal_debug', 'delta差价缩小，回归正常值，对头寸进行获利了结；卖掉之前买入，买回之前卖出' )
                        self.leave_market(self.stockid_1, sell_infos_1, self.stockid_2, buy_infos_2, current_delta_relative_prices[2])
                        continue

                    if current_delta_relative_prices[2] is not None and (0-current_delta_relative_prices[2]) > self.get_delta_threshold_of_stopping_loss():
                        log('deal_debug', 'delta差价继续拉大，达到给定阈值，进行止损；卖掉之前买入，买回之前卖出；' )
                        self.leave_market(self.stockid_1, sell_infos_1, self.stockid_2, buy_infos_2, current_delta_relative_prices[2])
                        continue

                    if self.minutes_to_closemarket <= self.stoploss_minutes_to_closemarket:
                        log('deal_debug', 'delta差价没有缩小，距离今日收盘仅剩'+str(self.stoploss_minutes_to_closemarket)+'分钟，强制对头寸进行了结；卖掉之前买入，买回之前卖出；' )
                        self.leave_market(self.stockid_1, sell_infos_1, self.stockid_2, buy_infos_2, current_delta_relative_prices[2])
                        continue


