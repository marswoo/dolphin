#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Util import *
import math, time, datetime
import os.path
import traceback

class OnesideDolphin(object):
    def __init__(self, pairid, data_feeder, account):
        self.pairid = pairid
        self.stock_pair = pairid.split('_')
        self.stockid_1 = self.stock_pair[0]
        self.stockid_2 = self.stock_pair[1]
        self.stockdata_1 = None
        self.stockdata_2 = None
        self.today_close_tag = False
        self.expense_each_deal = 20000.0
        self.buy_strategy_category = {'Buy_low':0, 'Buy_high':1}
        self.buy_strategy = self.buy_strategy_category['Buy_low']
        self.data_feeder = data_feeder
        self.account = account
        self.base_enter_threshold = 0.013
        self.yesterday_position_file = '/tmp/OnesideDolphin/YesterdayPosition/' + self.pairid
        os.system("mkdir -p /tmp/OnesideDolphin/YesterdayPosition/")
        if not os.path.isfile(self.yesterday_position_file):
            open(self.yesterday_position_file, 'w').write(str((0, 0, 0, 0, 0, 0)))

        self.new_day()


    def new_day(self):
        self.today_date = str(datetime.date.today())
        ''' 0: haven't done any deal this day; 
            1: already bought stock id1; 
            2: already bought stock id2; 
            3: already done deal today, only read data;
        '''
        self.today_bought_stock = 0
        self.today_buy_price = -1
        self.today_bought_amount = 0
        self.profit = 0
        self.minutes_to_closemarket = 241
        self.max_delta_of_today = [0.0]*3
        self.min_delta_of_today = [0.0]*3
        ''' [0] not used; 
            [1] represents delta for buy 1(low)
            [2] represents delta for buy 2(low)
        '''
        self.current_delta_relative_prices = [0.0]*3
        self.current_stock_delta = [0.0]*3
        self.last_stock_delta = [0.0]*3
        self.if_enter_triggered = 0
         
        log('debug_info', self.account.get_account_info())


    def close_today(self):
        # save today's trade record
        today_trades = self.account.get_today_trades()
        for trade in today_trades:
            if trade[2] in (self.stockid_1, self.stockid_2):
                log('realdeal_info', '\t'.join([str(item) for item in trade]))

        # update position information
        self.update_volatility()
        position = None
        if self.today_bought_stock in [1, 2]:
            position = (self.today_bought_stock, self.pairid.split('_')[ self.today_bought_stock - 1 ], self.today_buy_price, self.today_bought_amount, self.volatility[0], self.volatility[1])
        else:
            position = (0, 0, 0, 0, self.volatility[0], self.volatility[1])
        open(self.yesterday_position_file, 'w').write(str(position))


    def update_volatility(self):
        if self.stockdata_1 is None or self.stockdata_2 is None:
            return
        today_range = [max(stock_data['today_highest_price']-stock_data['today_lowest_price'], stock_data['today_highest_price']-stock_data['yesterday_close_price'], stock_data['yesterday_close_price']-stock_data['today_lowest_price']) / stock_data['yesterday_close_price'] for stock_data in (self.stockdata_1, self.stockdata_2)]
        for i in [0, 1]:
            if self.volatility[i] == 0:
                self.volatility[i] = round(today_range[i], 4)
            else:
                self.volatility[i] = round((9*self.volatility[i]+today_range[i]) / 10, 4)


    ''' 检查这个pair是否有重大新闻，如有则不进行交易 '''
    def check_big_news(self):
        if if_has_big_news(self.pairid, self.today_date):
            self.today_bought_stock = -1


    ''' 判断是否入场 '''
    def if_enter_market(self, want_buy_stock_index):
        return self.current_stock_delta[3-want_buy_stock_index] >= 0.025 \
                and self.max_delta_of_today[3-want_buy_stock_index]-self.current_stock_delta[3-want_buy_stock_index] < 0.01 \
                and (self.current_stock_delta[want_buy_stock_index] - self.min_delta_of_today[want_buy_stock_index] >= 0.01 or self.current_stock_delta[want_buy_stock_index] >= 0) \
                and self.current_stock_delta[want_buy_stock_index] < 0.025 \
                and self.current_delta_relative_prices[want_buy_stock_index] >= self.get_delta_threshold_of_entering_market()


    ''' 判断清仓的时机是否好 '''
    def if_leave_time_right(self):
#        if self.minutes_to_closemarket > 235:
#            return False
        #log("debug", "if_leave_time_right: %s, %s, %s"%(str(self.minutes_to_closemarket), str(self.if_enter_triggered), str(self.want_sell_index)))
        if self.minutes_to_closemarket <= 5:
            return True
        if not self.if_enter_triggered:
            if self.current_stock_delta[self.want_sell_index] >= 0.025 or self.current_delta_relative_prices[3-self.want_sell_index] >= 0.01:
                self.if_enter_triggered = 1
            return False
        else:
            stock_data = (None, self.stockdata_1, self.stockdata_2)[self.want_sell_index]
            if stock_data['sell_1_price'] == 0:
                return False
            return (stock_data['sell_1_price'] - stock_data['buy_1_price']) / stock_data['sell_1_price'] <= 0.0025 \
                and self.current_stock_delta[self.want_sell_index] < self.last_stock_delta[self.want_sell_index] \
                and self.max_delta_of_today[self.want_sell_index] - self.current_stock_delta[self.want_sell_index] >= 0.005


    '''
    入市条件中，两个Stock涨跌幅delta的阈值，随时间段变化
    '''
    def get_delta_threshold_of_entering_market(self):
        base = self.base_enter_threshold
        enter_threshold = [([240, 235], base-0.006), ([235, 210], base-0.004), ([210, 180], base-0.002), ([180, 120], base), ([120, 0], 100)]
        for threshold in enter_threshold:
            if self.minutes_to_closemarket > threshold[0][1] and self.minutes_to_closemarket <=  threshold[0][0]:
                return threshold[1]
         
        return 100


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
        if already_buy_unit_amount == want_unit_amount and already_buy_unit_amount != 0:
            deal_buy_price = total_cost / already_buy_unit_amount

        # sell deal price
        already_own_unit_amount = 0
        if stock_data['id'] == self.want_sell_stockid:
            already_own_unit_amount = self.want_sell_stock_amount / 100
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
        if already_sell_unit_amount == want_unit_amount and already_sell_unit_amount != 0:
            deal_sell_price = total_cost / already_sell_unit_amount

        return deal_buy_price, buy_infos, deal_sell_price, sell_infos


    def buy(self, stockid, buy_infos):
        buyprice, buynum = self.account.buy(stockid, buy_infos)
        if buynum > 0:
            log('buy_info', '\t'.join([ self.today_date+' '+self.stockdata_1['time'], '0', stockid, str(buyprice), str(buynum), '0' ]) )
        self.today_buy_price = buyprice
        self.today_bought_amount = buynum
        

    def sell(self, stockid, sell_infos):
        sellprice, sellnum = self.account.sell(stockid, sell_infos)
        if sellnum > 0:
            log('sell_info', '\t'.join([ self.today_date+' '+self.stockdata_1['time'], '1', stockid, str(sellprice), str(sellnum), '0' ]) )
        return sellprice, sellnum


    def log_stockdata(self):
        for stock_data in (self.stockdata_1, self.stockdata_2):
            record = '\t'.join([ 
                stock_data['id'],  self.today_date, stock_data['time'],
                str(stock_data['current_price']),
                str(stock_data['yesterday_close_price']), str(stock_data['today_open_price']),
                str(stock_data['today_highest_price']), str(stock_data['today_lowest_price']),
                str(stock_data['volume']), str(stock_data['turnover']),
                str(stock_data['buy_1_price']), str(stock_data['buy_1_amount']),
                str(stock_data['buy_2_price']), str(stock_data['buy_2_amount']),
                str(stock_data['buy_3_price']), str(stock_data['buy_3_amount']),
                str(stock_data['sell_1_price']), str(stock_data['sell_1_amount']),
                str(stock_data['sell_2_price']), str(stock_data['sell_2_amount']),
                str(stock_data['sell_3_price']), str(stock_data['sell_3_amount'])
            ])
            log('stock_realdata', record)

    
    ''' 得到昨日的仓位 '''
    def get_yesterday_position(self):
        yesterday_position = eval(open(self.yesterday_position_file, 'r').read())
        #log("debug", "yesterday_position: "+str(yesterday_position))
        self.want_sell_index = int(yesterday_position[0])
        self.want_sell_stockid = yesterday_position[1]
        self.want_sell_stock_enter_price = float(yesterday_position[2])
        self.want_sell_stock_amount = int(yesterday_position[3])
        self.volatility = [float(yesterday_position[4]), float(yesterday_position[5])]
        log('debug_info', self.today_date + ' volatility: '+str(self.volatility))

   
    ''' 卖掉昨天买入的 '''
    def clear_yesterday_position(self, sell_infos_list):
        sellprice, sellnum = self.sell(self.want_sell_stockid, sell_infos_list[self.want_sell_index])

        profit = self.want_sell_stock_amount * (sellprice - self.want_sell_stock_enter_price)
        self.profit = profit - 32   # 减去手续费，粗略估计值
        record = '\t'.join([self.pairid, self.today_date, str(self.profit), str(self.profit), '0'])
        log('asset_info', record)
        self.want_sell_index = 0

    
    ''' get profit from virtual deal '''
    def get_virtual_profit(self):
        return self.profit


    ''' get stock meta information '''    
    def get_stock_data(self):
        # 每隔2s获取一次数据
        time.sleep(4)

        # 计算得到当前时间，距离当天收市的时间，分钟表示
        now_time = strftime('%H:%M:%S', localtime())
        self.minutes_to_closemarket = get_minutes_to_closemarket(now_time)
        #log('debug', "self.minutes_to_closemarket: "+str(self.minutes_to_closemarket))

        if self.minutes_to_closemarket == -1:
            return False
        elif self.minutes_to_closemarket == 1 and not self.today_close_tag:
            self.today_close_tag = True
            self.close_today()
        elif self.minutes_to_closemarket == 120.5:
            wait_for_half_open()
            return True
        
        self.stockdata_1 = self.data_feeder.get_data(self.stockid_1)
        self.stockdata_2 = self.data_feeder.get_data(self.stockid_2)

        if None in (self.stockdata_1, self.stockdata_2):#可能停牌，可能发生异常
            return False
            
        return True


    ''' run dolphin to a pair of stocks '''
    def run(self):
        #self.check_big_news()
        self.get_yesterday_position()

        while True:
            self.last_stock_delta[1] = self.current_stock_delta[1]
            self.last_stock_delta[2] = self.current_stock_delta[2]
            if not self.get_stock_data():
                log('error', ' not self.get_stock_data')
                break

            stockdata_1 = self.stockdata_1
            stockdata_2 = self.stockdata_2

            if stockdata_1 is None or stockdata_2 is None or stockdata_1['current_price'] == 0 or stockdata_2['current_price'] == 0:
                log('GetStockData_error', ' Get Stock data error!')
                if None not in (stockdata_1, stockdata_2):
                    print stockdata_1['current_price'], stockdata_2['current_price']
                continue
            else:
                self.log_stockdata()
            
            current_buy_price_id_1, buy_infos_1, current_sell_price_id_1, sell_infos_1 = self.get_deal_price(stockdata_1)
            current_buy_price_id_2, buy_infos_2, current_sell_price_id_2, sell_infos_2  = self.get_deal_price(stockdata_2)

            # something is wrong with the stock metadata
            if current_buy_price_id_1 == -1 or current_sell_price_id_1 == -1 or current_buy_price_id_2 == -1 or current_sell_price_id_2 == -1:
                continue

            # calculate delta1 and delta2
            current_relative_price_id_1 = (current_buy_price_id_1 - stockdata_1['yesterday_close_price']) / stockdata_1['yesterday_close_price']
            current_relative_price_id_2 = (current_sell_price_id_2 - stockdata_2['yesterday_close_price']) / stockdata_2['yesterday_close_price']
            if math.fabs(current_relative_price_id_1) > 0.11 or math.fabs(current_relative_price_id_2) > 0.11:
                log('delta_error', 'data overflow')
                continue
            self.current_delta_relative_prices[1] = round(current_relative_price_id_2 - current_relative_price_id_1, 4)

            current_relative_price_id_1 = (current_sell_price_id_1 - stockdata_1['yesterday_close_price']) / stockdata_1['yesterday_close_price']
            current_relative_price_id_2 = (current_buy_price_id_2 - stockdata_2['yesterday_close_price']) / stockdata_2['yesterday_close_price']
            if math.fabs(current_relative_price_id_1) > 0.11 or math.fabs(current_relative_price_id_2) > 0.11:
                log('delta_error', 'data overflow')
                continue
            self.current_delta_relative_prices[2] = round(current_relative_price_id_1 - current_relative_price_id_2, 4)
        
            log('delta_info', '\t'.join([ self.pairid, self.today_date+' '+stockdata_1['time'], str(int(self.minutes_to_closemarket)), str(self.current_delta_relative_prices[1]), str(self.current_delta_relative_prices[2]) ]))
            
            self.max_delta_of_today[0] = max(self.max_delta_of_today[0], self.current_delta_relative_prices[1], self.current_delta_relative_prices[2])
            self.min_delta_of_today[0] = min(self.min_delta_of_today[0], self.current_delta_relative_prices[1], self.current_delta_relative_prices[2])
            self.current_stock_delta[1] = (stockdata_1['current_price'] - stockdata_1['yesterday_close_price']) / stockdata_1['yesterday_close_price']
            self.max_delta_of_today[1] = max(self.max_delta_of_today[1], self.current_stock_delta[1])
            self.min_delta_of_today[1] = min(self.min_delta_of_today[1], self.current_stock_delta[1])
            self.current_stock_delta[2] = (stockdata_2['current_price'] - stockdata_2['yesterday_close_price']) / stockdata_2['yesterday_close_price']
            self.max_delta_of_today[2] = max(self.max_delta_of_today[2], self.current_stock_delta[2])
            self.min_delta_of_today[2] = min(self.min_delta_of_today[2], self.current_stock_delta[2])

            if self.want_sell_index != 0 and self.if_leave_time_right():
                log('deal_debug', '达到退出条件，clear yesterday position')
                self.clear_yesterday_position((None, sell_infos_1, sell_infos_2))
                log("debug", "clear_yesterday_position over")

            # 当天尚未交易
            if self.today_bought_stock == 0:
                for want_buy_stock_index in [1, 2]:
                    if self.if_enter_market(want_buy_stock_index):
                        log('deal_debug', 'delta差价足够大，达到给定阈值，建立头寸；' )
                        self.delta_relative_price_when_entering_market = self.current_delta_relative_prices[want_buy_stock_index]
                        # 买低和买高不同的策略
                        if self.buy_strategy == self.buy_strategy_category['Buy_high']:
                            want_buy_stock_index = 3 - want_buy_stock_index
                        self.buy(self.stock_pair[want_buy_stock_index-1], (buy_infos_1, buy_infos_2)[want_buy_stock_index-1])

                        self.today_bought_stock = want_buy_stock_index
                        break


