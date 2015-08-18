#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Util import *
import math, time, datetime
import os.path
import traceback
import os
import scripts.api_util as api_util
import conf.dolphin_conf as dolphin_conf

class OnesideDolphin(object):
    def __init__(self, pairid, data_feeder, account, log_name = None):
        if log_name is not None:
            self.init_logging(log_name)
        else:
            self.init_logging(pairid)
        self.get_stock_data_error_cnt = 0
        self.get_stock_data_error_flag = True
        self.is_exp = False
        self.money_reserved = 0
        self.trader = None
        self.pairid = pairid
        self.stock_pair = pairid.split('_')
        self.stockid_1 = self.stock_pair[0]
        self.stockid_2 = self.stock_pair[1]
        self.stockdata_1 = None
        self.stockdata_2 = None
        self.dump_tag = True
        self.stop_buy_cnt = 0
        self.one_frame_ok = False #判断是否完成一帧数据的获取
        self.stop_buy = 0
        self.today_close_tag = False
        self.expense_each_deal = 20000.0
        self.buy_strategy_category = {'Buy_low':0, 'Buy_high':1}
        self.buy_strategy = self.buy_strategy_category['Buy_low']
        self.data_feeder = data_feeder
        self.account = account
        self.base_enter_threshold = 0.013
        self.check_dump_flag = True
        self.yesterday_position_file = '/tmp/OnesideDolphin/YesterdayPosition/' + self.pairid
        os.system("mkdir -p /tmp/OnesideDolphin/YesterdayPosition/")
        if not os.path.isfile(self.yesterday_position_file):
            self.init_status()
            #open(self.yesterday_position_file, 'w').write("empty=True")

        self.new_day()
        self.load_status()

    def set_exp(self):
        self.is_exp = True

    def init_logging(self, pairid):
        logger_name = pairid
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False # its parent will not print log (especially when client use a 'root' logger)

        fh = logging.FileHandler('dolphin/log/' + logger_name)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        global g_logger
        g_logger = logger


    ''' log message '''
    def log(self, category, message):
        message = str(message)
        message = category + "" + message

        if g_logger is not None:
            if category.find('info') != -1:
                g_logger.info(message)
            elif category.find('warning') != -1:
                g_logger.warning(message)
            elif category.find('debug') != -1:
                g_logger.debug(message)
            elif category.find('error') != -1:
                g_logger.error(message)
        
        if g_if_store2database:
            store_to_database(category, message)

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
        self.max_delta_of_today = [-0.1]*3
        self.min_delta_of_today = [0.1]*3
        self.min_span_delta_of_today = [1.0] * 3 
        ''' [0] not used; 
            [1] represents delta for buy 1(low)
            [2] represents delta for buy 2(low)
        '''
        self.current_delta_relative_prices = [0.0]*3
        self.current_stock_delta = [0.0]*3
        self.last_stock_delta = [0.0]*3
        self.if_enter_triggered = 0
         
        self.log('debug_info', self.account.get_account_info())


    def close_today(self):
        # save today's trade record
        today_trades = self.account.get_today_trades()
        if len(today_trades) == 0:
            today_trades = self.account.get_today_trades()

        for trade in today_trades:
            if trade[2] in (self.stockid_1, self.stockid_2):
                self.log('realdeal_info', '\t'.join([str(item) for item in trade]))

        # update position information
        self.update_volatility()
        self.dump_status(False)

    
    def dump_status(self, flag=True):
        status = []
        if flag:
            status.append("self.today_bought_stock = %s" % str(self.today_bought_stock))
            status.append("self.today_buy_price = %s" % str(self.today_buy_price))
            status.append("self.today_bought_amount = %s" % str(self.today_bought_amount))
            status.append("self.profit = %s" % str(self.profit))
            status.append("self.max_delta_of_today = %s" % str(self.max_delta_of_today))
            status.append("self.min_delta_of_today = %s" % str(self.min_delta_of_today))
            status.append("self.min_span_delta_of_today = %s" % str(self.min_span_delta_of_today))
            status.append("self.if_enter_triggered = %s" % str(self.if_enter_triggered))
            status.append("self.want_sell_index = %s" % str(self.want_sell_index))
            status.append("self.want_sell_stockid = '%s'" % str(self.want_sell_stockid))
            status.append("self.want_sell_stock_enter_price = %s" % str(self.want_sell_stock_enter_price))
            status.append("self.want_sell_stock_amount = %s" % str(self.want_sell_stock_amount))
            status.append("self.volatility = %s" % str(self.volatility))
            status.append("self.stop_buy = %s" % str(self.stop_buy))
        else:
            status.append("self.today_bought_stock = 0")
            status.append("self.today_buy_price = -1")
            status.append("self.today_bought_amount = 0")
            status.append("self.profit = 0")
            status.append("self.max_delta_of_today = [-0.1]*3")
            status.append("self.min_delta_of_today = [0.1]*3")
            status.append("self.min_span_delta_of_today = [0.1]*3")
            status.append("self.if_enter_triggered = 0")
            status.append("self.want_sell_index = %s" % str(self.today_bought_stock))
            status.append("self.want_sell_stockid = '%s'" % str(self.pairid.split('_')[ self.today_bought_stock - 1 ]))
            status.append("self.want_sell_stock_enter_price = %s" % str(self.today_buy_price))
            status.append("self.want_sell_stock_amount = %s" % str(self.today_bought_amount))
            status.append("self.volatility = %s" % str(self.volatility))
            status.append("self.stop_buy = %s" % str(self.stop_buy))

        #self.log("debug_dumpstatus", "dump_status flag: " + str(flag) + "\n" + "\n".join(status))
        open(self.yesterday_position_file, 'w').write("\n".join(status))


    def init_status(self):
        status = []
        status.append("self.today_bought_stock = 0") 
        status.append("self.today_buy_price = -1") 
        status.append("self.today_bought_amount = 0") 
        status.append("self.profit = 0") 
        status.append("self.max_delta_of_today = [-0.1]*3") 
        status.append("self.min_delta_of_today = [0.1]*3") 
        status.append("self.min_span_delta_of_today = [1.0]*3") 
        status.append("self.if_enter_triggered = 0") 
        status.append("self.want_sell_index = 0") 
        status.append("self.want_sell_stockid = 0") 
        status.append("self.want_sell_stock_enter_price = 0") 
        status.append("self.want_sell_stock_amount = 0") 
        status.append("self.volatility = [0,0]") 
        status.append("self.stop_buy = 0") 
        open(self.yesterday_position_file, 'w').write("\n".join(status))

   
    def load_status(self):
        data = [i for i in open(self.yesterday_position_file, 'r').read().split("\n") if i != ""]
        #self.log("debug_loadstatus", "debug_loadstatus: \n" + "\n".join(data))
        self.today_bought_stock = eval(data[0].split('=')[1].strip())
        self.today_buy_price = eval(data[1].split('=')[1].strip())
        self.today_bought_amount = eval(data[2].split('=')[1].strip())
        self.profit = eval(data[3].split('=')[1].strip())
        self.max_delta_of_today = eval(data[4].split('=')[1].strip())
        self.min_delta_of_today = eval(data[5].split('=')[1].strip())
        self.min_span_delta_of_today = eval(data[6].split('=')[1].strip())
        self.if_enter_triggered = eval(data[7].split('=')[1].strip())
        self.want_sell_index = eval(data[8].split('=')[1].strip())
        self.want_sell_stockid = eval(data[9].split('=')[1].strip())
        self.want_sell_stock_enter_price = eval(data[10].split('=')[1].strip())
        self.want_sell_stock_amount = eval(data[11].split('=')[1].strip())
        self.volatility = eval(data[12].split('=')[1].strip())
        if len(data) >= 14:
            self.stop_buy = eval(data[13].split('=')[1].strip())
        else:
            self.stop_buy = 0

    def check_dump(self, time1, time2):
        time1 = datetime.datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
        time2 = datetime.datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        delta1 = now - time1
        delta2 = now - time2
        if delta1.seconds > 45 or delta2.seconds > 45:
            if self.check_dump_flag:
                self.dump_status()
                self.check_dump_flag = False

    def check_stop_buy(self):
        #if self.minutes_to_closemarket <= 2 and abs(self.current_stock_delta[1] - self.current_stock_delta[2]) > 0.05:
        #    self.stop_buy_cnt += 1
        #    if self.stop_buy_cnt >= 3:
        #        self.log('debug', 'self.stop_buy!!! %s %s' % (str(self.current_stock_delta[1]), str(self.current_stock_delta[2])))
        #        self.stop_buy = 1
        #    else:
        #        self.stop_buy = 0
        pass

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
            self.log("stop_buy_debug", "there's big news " + self.pairid + " " + str(self.today_date))
            self.stop_buy = 1


    ''' 判断是否入场 '''
    def if_enter_market(self, want_buy_stock_index):
        if self.current_stock_delta[3-want_buy_stock_index] >= 0.025 \
                and self.max_delta_of_today[3-want_buy_stock_index]-self.current_stock_delta[3-want_buy_stock_index] < 0.01 \
                and (self.current_stock_delta[want_buy_stock_index] - self.min_delta_of_today[want_buy_stock_index] >= 0.01 or self.current_stock_delta[want_buy_stock_index] >= 0) \
                and self.current_stock_delta[want_buy_stock_index] < 0.025 \
                and self.current_delta_relative_prices[want_buy_stock_index] >= self.get_delta_threshold_of_entering_market():
            debug_data = []
            debug_data.append(str(self.current_stock_delta[3-want_buy_stock_index]))
            debug_data.append(str(self.max_delta_of_today[3-want_buy_stock_index]-self.current_stock_delta[3-want_buy_stock_index]))
            debug_data.append(str(self.current_stock_delta[want_buy_stock_index] - self.min_delta_of_today[want_buy_stock_index]))
            debug_data.append(str(self.current_stock_delta[want_buy_stock_index]))
            debug_data.append(str(self.current_stock_delta[want_buy_stock_index]))
            debug_data.append(str(self.current_delta_relative_prices[want_buy_stock_index]) + " " + str(self.get_delta_threshold_of_entering_market()))
            self.log("info_buy", "买入\n" + "\n".join(debug_data))
            return True
        else:
            return False


    ''' 判断清仓的时机是否好 '''
    def if_leave_time_right(self):
#        if self.minutes_to_closemarket > 235:
#            return False
        #self.log("debug", "if_leave_time_right: %s, %s, %s"%(str(self.minutes_to_closemarket), str(self.if_enter_triggered), str(self.want_sell_index)))
        if self.minutes_to_closemarket <= 7:
            return True
        #if not self.if_enter_triggered:
        if False:
            if self.current_stock_delta[self.want_sell_index] >= 0.025 or self.current_delta_relative_prices[3-self.want_sell_index] >= 0.01:
                debug_data = []
                debug_data.append(str(self.current_stock_delta[self.want_sell_index]))
                debug_data.append(str(self.current_delta_relative_prices[3-self.want_sell_index]))
                self.log("info_sell", "卖出trigger\n" + "\n".join(debug_data))
                self.if_enter_triggered = 1
            return False
        else:
            stock_data = (None, self.stockdata_1, self.stockdata_2)[self.want_sell_index]
            if stock_data['sell_1_price'] == 0:
                return False
            if (stock_data['sell_1_price'] - stock_data['buy_1_price']) / stock_data['sell_1_price'] <= 0.0025 \
                and self.current_stock_delta[self.want_sell_index] < self.last_stock_delta[self.want_sell_index] \
                and self.max_delta_of_today[self.want_sell_index] - self.current_stock_delta[self.want_sell_index] >= 0.005:
                debug_data = []
                debug_data.append(str((stock_data['sell_1_price'] - stock_data['buy_1_price']) / stock_data['sell_1_price']))
                debug_data.append(str(self.current_stock_delta[self.want_sell_index]) + " " + str(self.last_stock_delta[self.want_sell_index]))
                debug_data.append(str(self.max_delta_of_today[self.want_sell_index] - self.current_stock_delta[self.want_sell_index]))
                self.log("info_sell", "卖出\n" + "\n".join(debug_data))
                return True
            else:
                return False


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
            self.log('buy_info', '\t'.join([ self.today_date+' '+self.stockdata_1['time'], '0', stockid, str(buyprice), str(buynum), '0' ]) )
        self.today_buy_price = buyprice
        self.today_bought_amount = buynum
        

    def sell(self, stockid, sell_infos):
        sellprice, sellnum = self.account.sell(stockid, sell_infos)
        if sellnum > 0:
            self.log('sell_info', '\t'.join([ self.today_date+' '+self.stockdata_1['time'], '1', stockid, str(sellprice), str(sellnum), '0' ]) )
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
            self.log('stock_realdata', record)

    
    ''' 得到昨日的仓位 已废弃 '''
    def get_yesterday_position(self):
        yesterday_position = eval(open(self.yesterday_position_file, 'r').read())
        #self.log("debug", "yesterday_position: "+str(yesterday_position))
        self.want_sell_index = int(yesterday_position[0])
        self.want_sell_stockid = yesterday_position[1]
        self.want_sell_stock_enter_price = float(yesterday_position[2])
        self.want_sell_stock_amount = int(yesterday_position[3])
        self.volatility = [float(yesterday_position[4]), float(yesterday_position[5])]
        self.log('debug_info', self.today_date + ' volatility: '+str(self.volatility))

   
    ''' 卖掉昨天买入的 '''
    def clear_yesterday_position(self, sell_infos_list):
        sellprice, sellnum = self.sell(self.want_sell_stockid, sell_infos_list[self.want_sell_index])

        profit = self.want_sell_stock_amount * (sellprice - self.want_sell_stock_enter_price)
        self.profit = profit - 32   # 减去手续费，粗略估计值
        record = '\t'.join([self.pairid, self.today_date, str(self.profit), str(self.profit), '0'])
        self.log('asset_info', record)
        self.want_sell_index = 0
        self.dump_status()

    
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
        #self.log('debug', "self.minutes_to_closemarket: "+str(self.minutes_to_closemarket))

        if self.minutes_to_closemarket == -1:
            return -1
        elif self.minutes_to_closemarket == 1 and not self.today_close_tag:
            self.today_close_tag = True
            self.close_today()
        elif self.minutes_to_closemarket == 120.5:
            wait_for_half_open(self.log)
            return True
        
        self.stockdata_1 = self.data_feeder.get_data(self.stockid_1)
        self.stockdata_2 = self.data_feeder.get_data(self.stockid_2)

        if None in (self.stockdata_1, self.stockdata_2):#可能停牌，可能发生异常
            error_msg = "get_stock_data error! " + self.stockid_1 + "_" + self.stockid_2
            self.get_stock_data_error_cnt += 1
            if self.get_stock_data_error_cnt > 100 and self.get_stock_data_error_flag:
                print os.popen("cd /root/mail_notify/src && python mail_simple.py 'woody213@yeah.net;80382133@qq.com' 'get_stock_data_error " + self.pairid + "' 'rt'").read()
                self.get_stock_data_error_flag = False
            return False
            
        return True


    #获取挡圈可用金额
    def update_money_reserved(self):
        if not self.is_exp:
            try:
                self.trader = api_util.get_trader()
                self.trader.update_account_info()
                time.sleep(2)
                info = self.trader.get_account_info()
                self.money_reserved = float(info["Available"])
                self.log("info", "money_reserved: " + str(self.money_reserved))
            except:
                self.log("error", "get money_reserved fail!!! " + traceback.format_exc())
                pass


    ''' run dolphin to a pair of stocks '''
    def run(self):
        self.log("debug", "run!!!")
        self.load_status()
        self.check_big_news()
        error_count = 0
        error_count_all = 0

        while True:
            self.last_stock_delta[1] = self.current_stock_delta[1]
            self.last_stock_delta[2] = self.current_stock_delta[2]
            rt = self.get_stock_data()
            if self.minutes_to_closemarket == 1 and rt is False:
                error_count += 1
            if error_count > 10:
                break
            if error_count_all > 100:
                break
            if rt is False:
                error_count_all += 1
                #self.log('error', ' not self.get_stock_data' + " " + str(self.minutes_to_closemarket) + " " + str(error_count_all))
                continue
            if rt == -1:
                break

            #每两分钟dump_status
            if int(self.minutes_to_closemarket) % 2 == 0 and self.dump_tag == True:
                self.dump_status()
                self.dump_tag = False
            elif int(self.minutes_to_closemarket) % 2 != 0:
                self.dump_tag = True

            stockdata_1 = self.stockdata_1
            stockdata_2 = self.stockdata_2

            if stockdata_1 is None or stockdata_2 is None or stockdata_1['current_price'] == 0 or stockdata_2['current_price'] == 0:
                self.log('GetStockData_error', ' Get Stock data error!')
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
                self.log('delta_error', 'data overflow')
                continue
            self.current_delta_relative_prices[1] = round(current_relative_price_id_2 - current_relative_price_id_1, 4)

            current_relative_price_id_1 = (current_sell_price_id_1 - stockdata_1['yesterday_close_price']) / stockdata_1['yesterday_close_price']
            current_relative_price_id_2 = (current_buy_price_id_2 - stockdata_2['yesterday_close_price']) / stockdata_2['yesterday_close_price']
            if math.fabs(current_relative_price_id_1) > 0.11 or math.fabs(current_relative_price_id_2) > 0.11:
                self.log('delta_error', 'data overflow')
                continue
            self.current_delta_relative_prices[2] = round(current_relative_price_id_1 - current_relative_price_id_2, 4)
        
            self.log('delta_info', '\t'.join([ self.pairid, stockdata_1['date']+' '+stockdata_1['time'], str(int(self.minutes_to_closemarket)), str(self.current_delta_relative_prices[1]), str(self.current_delta_relative_prices[2]) ]))
            #self.log('delta_debug', '\t'.join([ self.pairid, stockdata_1['date']+' '+stockdata_1['time'], str(int(self.minutes_to_closemarket)), str(self.current_stock_delta[self.want_sell_index]), str(self.max_delta_of_today[self.want_sell_index]) ]))

            #判断delta时间是否和当前时间相差超过阈值，如果是，则dump当前指标准备重启
            self.check_dump(self.today_date+' '+stockdata_1['time'], self.today_date+' '+stockdata_2['time'])
            
            self.max_delta_of_today[0] = max(self.max_delta_of_today[0], self.current_delta_relative_prices[1], self.current_delta_relative_prices[2])
            self.min_delta_of_today[0] = min(self.min_delta_of_today[0], self.current_delta_relative_prices[1], self.current_delta_relative_prices[2])
            self.current_stock_delta[1] = (stockdata_1['current_price'] - stockdata_1['yesterday_close_price']) / stockdata_1['yesterday_close_price']
            self.max_delta_of_today[1] = max(self.max_delta_of_today[1], self.current_stock_delta[1])
            self.min_delta_of_today[1] = min(self.min_delta_of_today[1], self.current_stock_delta[1])
            self.min_span_delta_of_today[1] = min(self.min_span_delta_of_today[1], self.current_stock_delta[1] - self.current_stock_delta[2])
            self.current_stock_delta[2] = (stockdata_2['current_price'] - stockdata_2['yesterday_close_price']) / stockdata_2['yesterday_close_price']
            self.max_delta_of_today[2] = max(self.max_delta_of_today[2], self.current_stock_delta[2])
            self.min_delta_of_today[2] = min(self.min_delta_of_today[2], self.current_stock_delta[2])
            self.min_span_delta_of_today[2] = min(self.min_span_delta_of_today[2], self.current_stock_delta[2] - self.current_stock_delta[1])
            self.one_frame_ok = True

            if self.want_sell_index != 0 and self.if_leave_time_right():
                #send email
                os.popen("cd /root/mail_notify/src && python mail_simple.py 'woody213@yeah.net;80382133@qq.com' 'sell_stock: " + self.pairid.split("_")[self.want_sell_index - 1] + "' 'rt'").read()

                self.log('deal_debug', '达到退出条件，clear yesterday position')
                self.clear_yesterday_position((None, sell_infos_1, sell_infos_2))
                self.log("debug", "clear_yesterday_position over")

            #判断第二天是否会买入
            if self.one_frame_ok: #只有一帧完成后才去计算stop_buy，否则维持原样
                self.check_stop_buy()

            # 当天尚未交易
            if self.today_bought_stock == 0 and self.stop_buy == 0:

                for want_buy_stock_index in [1, 2]:
                    if self.if_enter_market(want_buy_stock_index):
                        if not self.is_exp:
                            self.update_money_reserved()
                        #检查是否超过预留资金限额
                        buy_money = 0.0
                        buy_info_t = (buy_infos_1, buy_infos_2)[want_buy_stock_index-1]
                        for (buy_price, buy_amount) in buy_info_t:
                            buy_money += buy_price * buy_amount
                        if not self.is_exp and self.money_reserved - buy_money < dolphin_conf.COMMON_CONF["money_reserved"]:
                            self.log("debug_money_reserved", "stop buy: " + str(self.money_reserved))
                            continue

                        self.log('deal_debug', 'delta差价足够大，达到给定阈值，建立头寸；' )
                        self.delta_relative_price_when_entering_market = self.current_delta_relative_prices[want_buy_stock_index]
                        # 买低和买高不同的策略
                        if self.buy_strategy == self.buy_strategy_category['Buy_high']:
                            want_buy_stock_index = 3 - want_buy_stock_index
                        self.buy(self.stock_pair[want_buy_stock_index-1], (buy_infos_1, buy_infos_2)[want_buy_stock_index-1])

                        self.today_bought_stock = want_buy_stock_index
                        self.dump_status()

                        #send email
                        os.popen("cd /root/mail_notify/src && python mail_simple.py 'woody213@yeah.net;80382133@qq.com' 'buy_stock: " + self.pairid.split("_")[want_buy_stock_index-1] + "' 'rt'").read()
                        break


