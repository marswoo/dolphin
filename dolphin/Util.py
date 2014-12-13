#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import *
from math import fabs
import logging, datetime, sys
import MySQLdb, urllib2
from warnings import filterwarnings
import traceback


##################################################################
''' all valid pair to run '''
candidate_stock_pairs = [ 
    # online
    'sh600216_sz002001',    # 医药
    'sh601801_sh601999',    # 传媒
    'sz002136_sz002601',    # 钛白粉
    'sh600209_sz000735',    # 海南旅游岛
    'sh600389_sh600596',    # 金改
    'sz002441_sz300068',    # 电气设备
    'sh600017_sh601880',    # 港口
    'sh600884_sz002091',    # 动力锂电池
    'sh600880_sz300052',    # 手机游戏
    'sh600597_sh600887',    # 乳业
    'sh600789_sz002166',    # 生物制药
    'sh600435_sh600501',    # 航天军工
    'sh600639_sh600663',    # 园区开发
    'sh600391_sz000561',    # 航天军工
    'sh600031_sz000157',
    'sh600999_sh601788',
    'sz300042_sz300270',
    'sz002031_sz300193',
    'sh600343_sh600879',
    'sz000568_sz000858',
    'sz002279_sz002474',
#   'sh600199_sh600809',    # 酒类
#   'sz000021_sz000066',    # 电子设备
#   'sz000758_sz000993',    # 稀土
#   'sh600410_sz002544',
]


##################################################################
''' global information '''
g_logger = None
g_conn = None
g_cursor = None
g_if_store2database = True


##################################################################
''' some useful time functions '''

''' return seconds, time input format: %H:%M:%S '''
def get_time_interval_seconds(time1, time2):
    s1 = mktime(strptime('2013-01-01 '+time1, '%Y-%m-%d %H:%M:%S'))
    s2 = mktime(strptime('2013-01-01 '+time2, '%Y-%m-%d %H:%M:%S'))
    return fabs(s1 - s2)

''' return minutes from closing stock market, input time format: %H:%M:%S '''
def get_minutes_to_closemarket(time):
    open_time = mktime(strptime('2013-01-01 09:30:00', '%Y-%m-%d %H:%M:%S'))
    half_close_time = mktime(strptime('2013-01-01 11:30:00', '%Y-%m-%d %H:%M:%S'))
    half_open_time = mktime(strptime('2013-01-01 13:00:00', '%Y-%m-%d %H:%M:%S'))
    close_time = mktime(strptime('2013-01-01 15:00:00', '%Y-%m-%d %H:%M:%S'))
    now_time = mktime(strptime('2013-01-01 ' + time, '%Y-%m-%d %H:%M:%S'))
    if now_time < open_time:
        return 241
    elif now_time < half_close_time:
        return int(half_close_time-now_time)/60 + 60*2 + 1
    elif now_time < half_open_time:
        return 120.5
    elif now_time <= close_time:
        return int(close_time-now_time)/60 + 1
    else:
        return -1

##################################################################
''' get current stock price from sina service '''
def get_current_price(stockid):
    try:
        url = 'http://hq.sinajs.cn/list=%s' % stockid
        content = urllib2.urlopen(url).read()
        content = content[content.find('=')+2 : ]
        items = content.split(',')
        return float(items[3])
    except:
        return 0.0


''' get profit of pair in the database of experiment '''
def get_profit_of_pair(pairid, start_date, end_date):
    g_cursor.execute("SELECT sum(cash) FROM dolphin_asset where pairid=%s and date>=%s and date<%s and is_real=0", (pairid, start_date, end_date))
    r = g_cursor.fetchone()
    if r is not None:
        return float(r[0])
    else:
        return 0.0


##################################################################
''' For store useful information below '''

def reconnect_database(dbconf = None):
    global g_conn, g_cursor
    if g_conn:
        g_conn.commit()
        g_conn.close()
        g_conn = None
    g_conn = MySQLdb.connect(host = dbconf['HOST'], user = dbconf['USER'], passwd = dbconf['PASSWORD'], db = dbconf['NAME'], charset = 'utf8')
    g_conn.autocommit(True)
    g_cursor = g_conn.cursor()
    filterwarnings('ignore', category = MySQLdb.Warning)


def disable_store2database():
    global g_if_store2database
    g_if_store2database = False


def if_has_big_news(pairid, today_date):
    g_cursor.execute("SELECT label FROM dolphin_notificationnews WHERE pairid=%s and date=%s", (pairid, today_date))
    r = g_cursor.fetchone()
    if r is not None and int(r[0]) == 1:
        return True
    else:
        return False


''' store some information to database '''
def store_to_database(category, message):
    try:
        if category == 'delta_info':
            message = message.replace('None', '0.0')
        items = tuple(message.split('\t'))
        placeholder = ', '.join(['%s']*len(items))
        if category == 'delta_info':
            fields = 'pairid, timestamp, minutes_to_closemarket, delta1, delta2'
            g_cursor.execute('INSERT INTO dolphin_pairdelta (' + fields + ') VALUES (' + placeholder + ')', items)
        elif category == 'stock_realdata':
            fields = 'stockid, date, time, current_price, yesterday_close_price, today_open_price, today_highest_price, today_lowest_price, deal_stock_amount, deal_stock_money, buy1_price, buy1_amount, buy2_price, buy2_amount, buy3_price, buy3_amount, sell1_price, sell1_amount, sell2_price, sell2_amount, sell3_price, sell3_amount'
            g_cursor.execute('INSERT INTO dolphin_stockmetadata (' + fields + ') VALUES (' + placeholder + ')', items)
        elif category in ['buy_info', 'sell_info', 'realdeal_info']:
            fields = 'timestamp, is_buy, stockid, price, amount, is_real'
            g_cursor.execute('INSERT INTO dolphin_deal (' + fields + ') VALUES (' + placeholder + ')', items)
        elif category == 'asset_info':
            fields = 'pairid, date, cash, total, is_real'
            g_cursor.execute("select total from dolphin_asset where pairid = %s order by date desc limit 1", (items[0], ))
            res = g_cursor.fetchall()
            total = 0
            if len(res) != 0:
                total = res[0][0]
                items = list(items)
                items[3] = str(float(items[2]) + float(total))
                items = tuple(items)
                log("debug", "update dolphin_asset: total(before)=%s, profit=%s, total(after)=%s" % (str(total), str(items[2]), str(items[3])))
            g_cursor.execute('INSERT INTO dolphin_asset (' + fields + ') VALUES (' + placeholder + ')', items)
                
        elif category == 'news_info':
            fields = 'pairid, date, news, label'
            g_cursor.execute('INSERT INTO dolphin_notificationnews (' + fields + ') VALUES (' + placeholder + ')', items)
    except:
        print >> open("/tmp/OnesideDolphin/errorlog", "a"), traceback.format_exc()


''' init logging '''
def init_logging(pairid):
    logger_name = pairid
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False # its parent will not print log (especially when client use a 'root' logger)

    fh = logging.FileHandler('dolphin/log/' + logger_name)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)-15s %(levelname)s %(filename)s:%(lineno)s %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    global g_logger
    g_logger = logger

''' log message '''
def log(category, message):
    message = str(message)

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

##################################################################
''' Useful functions to wait when market is closed '''

def if_close_market_today(today_date):
    a = [int(i) for i in today_date.split('-')]
    weekday = datetime.datetime(a[0], a[1], a[2]).weekday()
    if weekday == 5 or weekday == 6:
        log('close_info', today_date + ' is weekend!')
        return True
#    reconnect_database()
    g_cursor.execute("select date from dolphin_marketclosedate where date>=%s", (today_date,))
    close_date_list = g_cursor.fetchall()
    close_date_list = [ str(i[0]) for i in close_date_list ]
    if today_date in close_date_list:
        log('close_info', today_date + ' is in close date list!')
        return True
        
    return False

def wait_for_next_open():
    # commit the database before today is over
    try:
        global g_conn
        if g_conn:
            g_conn.commit()
            g_conn.close()
            g_conn = None
    except:
        log('database_error', 'Database commit error')

    log('wait_info', "****************** wait for next open ******************" )
    now_seconds = time()
    now_time = strftime('%Y-%m-%d %H:%M:%S', localtime(now_seconds))
    next_open_date = now_time[:10]
    if int(now_time[11:13]) > 9 or (int(now_time[11:13]) == 9 and int(now_time[14:16]) >= 30):
        tomorrow_seconds = now_seconds + 24*3600
        next_open_date = strftime('%Y-%m-%d', localtime(tomorrow_seconds))
    next_open_time = next_open_date + " 09:30:00"
    next_open_seconds = mktime(strptime(next_open_time, '%Y-%m-%d %H:%M:%S'))
    log('wait_info', "****************** sleep " + str(next_open_seconds - now_seconds) + " seconds ******************" )
    sleep(next_open_seconds - now_seconds + 10)
    if if_close_market_today(datetime.date.today()):
        wait_for_next_open()


def wait_for_half_open():
    log('wait_info', "****************** wait for half open ******************" )
    now_seconds = time()
    now_time = strftime('%Y-%m-%d %H:%M:%S', localtime(now_seconds))
    next_open_date = now_time[:10]
    if int(now_time[11:13]) >= 13: 
        log('time_error', "The time has already passed the half open time 13:00:00" )
        return
    next_open_time = next_open_date + " 13:00:00"
    next_open_seconds = mktime(strptime(next_open_time, '%Y-%m-%d %H:%M:%S'))
    log('wait_info', "****************** sleep " + str(next_open_seconds - now_seconds) + " seconds ******************" )
    sleep(next_open_seconds - now_seconds)

##################################################################
''' Useful functions to log asset history '''

''' Judge if we need to update the deal record in the database according to the existing records in the database '''
def if_need_update_real_deal(pairid):
    stockid_1, stockid_2 = get_stockid_by_pairid(pairid)
    g_cursor.execute("SELECT MAX(DATE(timestamp)) FROM dolphin_deal where (stockid=%s or stockid=%s) and is_real=1", (stockid_1, stockid_2))
    max_date = g_cursor.fetchone()[0]
    today = str(datetime.date.today())
    if max_date is None or max_date == today:
        return False
    else:
        return True

'''
    update the asset of the pair in the database according to the deal record
'''
def update_asset(pairid, today_date, profit_by_delta):
    if not g_if_store2database:
        return
    stockid_1, stockid_2 = get_stockid_by_pairid(pairid)
    stock_num = {}
    for is_real in ['0', '1']:
        g_cursor.execute("SELECT MAX(date) FROM dolphin_asset where pairid=%s and is_real=%s", (pairid, is_real))
        one_item = g_cursor.fetchone()
        # in case this is a new pair
        if one_item[0] is None:
            g_cursor.execute("INSERT INTO dolphin_asset (pairid, date, cash, total, is_real) VALUES (%s, %s, '0.00', '0.00', %s)", (pairid, today_date, is_real))
            continue
        max_date = str(one_item[0])
        if max_date == today_date:
            continue
        g_cursor.execute("SELECT total FROM dolphin_asset WHERE date=%s and pairid=%s and is_real=%s LIMIT 1", (max_date, pairid, is_real))
        before_asset = float(g_cursor.fetchone()[0])

        cash = 0.0
        if is_real is '1':
            g_cursor.execute("SELECT is_buy, price, amount, stockid FROM dolphin_deal WHERE is_real=%s AND DATE(timestamp)=%s AND (stockid=%s or stockid=%s)", (is_real, today_date, stockid_1, stockid_2))
            records = g_cursor.fetchall()
            if len(records) != 4:
                continue
            for record in records:
                ''' in case the stock number of deals change '''
                if record[3] not in stock_num.keys():
                    stock_num[record[3]] = record[2]

                if record[0] == 0:
                    cash -= float(record[1] * stock_num[record[3]])
                else:
                    cash += float(record[1] * stock_num[record[3]])
                cash -= calculate_charge( int(record[0]), float(record[1]), int(stock_num[record[3]]), str(record[3]) )
        else:
            cash = profit_by_delta

        record = '\t'.join([pairid, today_date, str(cash), str(before_asset+cash), is_real])
        log('asset_info', record)

'''
    calculate the fee for buying and selling
'''
def calculate_charge(buy_or_sell, price, amount, stockid):
    charge = 0.0
    if buy_or_sell == 1:
        charge += price*amount*0.001
    charge += max(price*amount*0.0003, 5)
    if stockid.startswith('sh'):
        charge += amount * 0.01 * 0.06
    return charge


##################################################################
''' Useful small function '''

'''
    complete the whole name of stockid
    for example: 600516->sh600516
'''
def complete_stockid(stockid):
    if stockid.startswith(('0', '3')):
        return 'sz'+stockid
    elif stockid.startswith('6'):
        return 'sh'+stockid

''' get stockids from pairid '''
def get_stockid_by_pairid(pairid):
    return pairid.split('_')

'''
    init to buy some amount of stock in the pair
'''
def init_account(account, pairid):
    stockid_1, stockid_2 = get_stockid_by_pairid(pairid)
    is_real = '0'
    g_cursor.execute("SELECT MAX(date) FROM dolphin_asset where pairid=%s and is_real=%s", (pairid, is_real))
    one_item = g_cursor.fetchone()
    max_date = str(one_item[0])
    g_cursor.execute("SELECT is_buy, price, amount, stockid FROM dolphin_deal WHERE is_real=%s AND DATE(timestamp)=%s AND (stockid=%s or stockid=%s)", (is_real, max_date, stockid_1, stockid_2))
    records = g_cursor.fetchall()
    if len(records) != 4:
        return
    for record in records:
        if record[0] == 1:
            account.buy(record[3], [(float(record[1]), int(record[2]))])
    return


if __name__ == '__main__':
    #print get_current_price('sz000089')
    print get_minutes_to_closemarket('14:58:59')


