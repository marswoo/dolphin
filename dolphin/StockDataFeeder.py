#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from django.conf import settings
from conf.dbconf import dbconf
import urllib2, os, time
import MySQLdb
import Util
import sys
import traceback

class StockDataFeeder(object):
    def get_data(self, stockid):
        raise NotImplementedError( "Should have implemented this" )

class LocalWebServiceDataFeeder(StockDataFeeder):
    def __init__(self):
        pass
    
    def pack_stock_realdata(self, stockid, value_list):
        stock_data = {}
        stock_data['id'] = value_list[0]
        stock_data['date'] = value_list[1]
        stock_data['time'] = value_list[2]
        stock_data['current_price'] = float(value_list[3])
        stock_data['yesterday_close_price'] = float(value_list[4])
        stock_data['today_open_price'] = float(value_list[5])
        stock_data['today_close_price'] = float(value_list[6])
        stock_data['today_highest_price'] = float(value_list[7])
        stock_data['today_lowest_price'] = float(value_list[8])
        stock_data['volume'] = float(value_list[9])
        stock_data['turnover'] = float(value_list[10])
        stock_data['buy_1_price'] = float(value_list[11])
        stock_data['buy_1_amount'] = int(value_list[12])
        stock_data['buy_2_price'] = float(value_list[13])
        stock_data['buy_2_amount'] = int(value_list[14])
        stock_data['buy_3_price'] = float(value_list[15])
        stock_data['buy_3_amount'] = int(value_list[16])
        stock_data['sell_1_price'] = float(value_list[17])
        stock_data['sell_1_amount'] = int(value_list[18])
        stock_data['sell_2_price'] = float(value_list[19])
        stock_data['sell_2_amount'] = int(value_list[20])
        stock_data['sell_3_price'] = float(value_list[21])
        stock_data['sell_3_amount'] = int(value_list[22])
        return stock_data

    def get_data(self, stockid):
        try:
            url = 'http://127.0.0.1:8082/dolphin/get_stockdata/%s/' % stockid
            content = urllib2.urlopen(url).read()
            #if content.count("0,"*12) != 0: #停牌
            #    return None
            items = content.split(',')
            stock_data = self.pack_stock_realdata(stockid, items)
            
            return stock_data
        except:
            traceback.print_exc()   
            return None


class StockSinaRealDataFeeder(StockDataFeeder):
    def __init__(self):
        pass
    
    def pack_stock_sina_realdata(self, stockid, value_list):
        stock_data = {}
        stock_data['id'] = stockid
        stock_data['name'] = value_list[0]
        stock_data['today_open_price'] = float(value_list[1])
        stock_data['yesterday_close_price'] = float(value_list[2])
        stock_data['current_price'] = float(value_list[3])
        stock_data['today_highest_price'] = float(value_list[4])
        stock_data['today_lowest_price'] = float(value_list[5])
        stock_data['deal_stock_amount'] = int(value_list[8])
        stock_data['deal_stock_money'] = float(value_list[9])
        stock_data['buy_1_amount'] = int(value_list[10])
        stock_data['buy_1_price'] = float(value_list[11])
        stock_data['buy_2_amount'] = int(value_list[12])
        stock_data['buy_2_price'] = float(value_list[13])
        stock_data['buy_3_amount'] = int(value_list[14])
        stock_data['buy_3_price'] = float(value_list[15])
#        stock_data['buy_4_amount'] = int(value_list[16])
#        stock_data['buy_4_price'] = float(value_list[17])
#        stock_data['buy_5_amount'] = int(value_list[18])
#        stock_data['buy_5_price'] = float(value_list[19])
        stock_data['sell_1_amount'] = int(value_list[20])
        stock_data['sell_1_price'] = float(value_list[21])
        stock_data['sell_2_amount'] = int(value_list[22])
        stock_data['sell_2_price'] = float(value_list[23])
        stock_data['sell_3_amount'] = int(value_list[24])
        stock_data['sell_3_price'] = float(value_list[25])
#        stock_data['sell_4_amount'] = int(value_list[26])
#        stock_data['sell_4_price'] = float(value_list[27])
#        stock_data['sell_5_amount'] = int(value_list[28])
#        stock_data['sell_5_price'] = float(value_list[29])
        stock_data['date'] = value_list[30]
        stock_data['time'] = value_list[31]
        return stock_data

    def get_data(self, stockid):
        try:
            url = 'http://hq.sinajs.cn/list=%s' % stockid
            content = urllib2.urlopen(url).read()
            content = content[content.find('=')+2 : ]
            items = content.split(',')
            stock_data = self.pack_stock_sina_realdata(stockid, items)
            return stock_data
        except:
            return None


class StockHistoryMySQLDataFeeder(StockDataFeeder):
    def __init__(self, pairid, now_date):
        stockid_1, stockid_2 = Util.get_stockid_by_pairid(pairid)
        #self.conn = MySQLdb.connect(host = 'localhost', user='tf', passwd='tfpass', db='tf2')
        #dbconf = settings.DATABASES['default']
        self.conn = MySQLdb.connect(host = dbconf['HOST'], user = dbconf['USER'], passwd = dbconf['PASSWORD'], db = dbconf['NAME'], charset = 'utf8')
        self.now_date = now_date
        self.stockid_to_cursor = {}
        self.stockid_to_cursor[stockid_1] = self.conn.cursor()
        self.stockid_to_cursor[stockid_2] = self.conn.cursor()
        for stockid in self.stockid_to_cursor.keys():
            self.stockid_to_cursor[stockid].execute('select * from dolphin_stockmetadata where date=%s and stockid=%s order by time', (self.now_date, stockid))

    def pack_history_stock_data(self, stockid, row):
        stock_data = {}
        stock_data['id'] = stockid
        stock_data['date'] = str(row[2])
        stock_data['time'] = str(row[3])
        stock_data['current_price'] = float(row[4])
        stock_data['yesterday_close_price'] = float(row[5])
        stock_data['today_open_price'] = float(row[6])
        stock_data['today_highest_price'] = float(row[7])
        stock_data['today_lowest_price'] = float(row[8])
        stock_data['volume'] = int(row[9])
        stock_data['turnover'] = int(row[10])
        stock_data['buy_1_price'] = float(row[11])
        stock_data['buy_1_amount'] = int(row[12])
        stock_data['buy_2_price'] = float(row[13])
        stock_data['buy_2_amount'] = int(row[14])
        stock_data['buy_3_price'] = float(row[15])
        stock_data['buy_3_amount'] = int(row[16])
        stock_data['sell_1_price'] = float(row[17])
        stock_data['sell_1_amount'] = int(row[18])
        stock_data['sell_2_price'] = float(row[19])
        stock_data['sell_2_amount'] = int(row[20])
        stock_data['sell_3_price'] = float(row[21])
        stock_data['sell_3_amount'] = int(row[22])
        return stock_data

    def get_data(self, stockid):
        if stockid not in self.stockid_to_cursor.keys():
            raise Exception('Wrong stockid when fetching stock data from MySQL')
        
        row = self.stockid_to_cursor[stockid].fetchone()
        if not row:
            return None
        else:
            return self.pack_history_stock_data(stockid, row)
    

if __name__ == "__main__":
    import time
    import json
    feeder = StockSinaRealDataFeeder()
#    feeder = LocalWebServiceDataFeeder()
    while True:
        data = feeder.get_data('sh600663')
        for key in data:
            print key, data[key]
        break
        #print str(datetime.datetime.now())[11:-7], data['time'], data['buy_1_price'], data['buy_1_amount'], data['buy_2_price'], data['buy_2_amount'], data['buy_3_price'], data['buy_3_amount']


