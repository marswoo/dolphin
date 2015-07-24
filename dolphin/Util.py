#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import *
from math import fabs
import logging, datetime, sys
import MySQLdb, urllib2
from warnings import filterwarnings
import traceback
from conf import dbconf


##################################################################
''' all valid pair to run '''
candidate_stock_pairs = [ 
    # online
    'sh600216_sz002001',
    'sz002136_sz002601',
    'sh600108_sh601118', #亚盛集团 海南橡胶
    'sh600389_sh600596',
    'sz002441_sz300068',
    'sh600597_sh600887',
    'sh600501_sz002025',
    'sh600031_sz000157',
    'sz000568_sz000858',
    'sz002279_sz002474',
    'sz000333_sz000651',
    'sh601601_sh601628',
    'sh600720_sz000789', #祁连山/万年青
    'sz000001_sh601166', #/平安银行/兴业银行
    'sh600011_sh600027', #/华能国际/华电国际
    'sz000758_sh601168', #/中色股份/西部矿业
    'sz000088_sz000507', #/盐 田 港/珠海港   
    'sh600026_sh601866', #/中海发展/中海集运 
    'sh600639_sh600648', #浦东金桥/外高桥
    'sh601801_sh601928', #/皖新传媒/凤凰传媒
    "sh600737_sz000930", #/中粮屯河   /中粮生化   　  注释状态，暂不开启
    "sh600618_sh600636", #/氯碱化工   /三爱富 　  注释状态，暂不开启
    "sz000738_sz000768", #/中航动控   /中航飞机   　  注释状态，暂不开启
    "sh600545_sz002302", #/新疆城建   /西部建设   　  注释状态，暂不开启
    "sh600089_sh601179", #特变电工 中国西电",   
#    'sh600789_sz002166', #/鲁抗医药/莱茵生物 
#    'sh600884_sz002091', #杉杉股份 江苏国泰
#    'sh600343_sh600879',
#    'sh600831_sz000665', #广电网络/湖北广电
#    'sz002649_sz300079', #博彦科技/数码视讯
#    'sz000877_sh600425', #/天山股份/青松建化
#    'sh600199_sh600702', #/金种子酒/沱牌舍得 
#    'sh600048_sz000024', #/保利地产/招商地产
#   "sh600008_sz000598", #/首创股份   /兴蓉投资   　  注释状态，暂不开启
#   "sz002083_sz002087", #/孚日股份   /新野纺织   　  注释状态，暂不开启
#   "sh600354_sz000713", #/敦煌种业   /丰乐种业   　  注释状态，暂不开启
#   "sh600717_sh600751", #/天津港     /天津海运   　  注释状态，暂不开启
#   "sh600432_sz000693", #/吉恩镍业   /华泽钴镍   　  注释状态，暂不开启
#   "sh600261_sz000541", #/阳光照明   /佛山照明   　  注释状态，暂不开启
]

#   'sh600030_sh600837',
#   'sh600259_sz000831', #/广晟有色/五矿稀土 
#   'sh600757_sh601801', #/长江传媒/皖新传媒
#   'sh600633_sh601928', #/浙报传媒/凤凰传媒
#   'sh600639_sh600663',    # 浦东金桥 陆家嘴
#   'sh600199_sh600809', #/金种子酒/山西汾酒
#   'sh600017_sh601880',    # 日照港 大连港
#   'sh600999_sh601788',
#   'sz000021_sz000066',
#   'sh600789_sz002166',    # 鲁抗医药 莱茵生物
#   'sh601801_sh601999',    # 传媒
#   'sh600391_sz000561',    # 航天军工
#   'sz002031_sz300193',
#   'sh600199_sh600809',    # 酒类
#   'sz000021_sz000066',    # 电子设备
#   'sz000758_sz000993',    # 稀土
#   'sh600410_sz002544',
#   'sz300042_sz300270',

pairs_names	=	{	
"sh600737_sz000930":"sh600737	sz000930    中粮屯河   中粮生化", 
"sh600618_sh600636":"sh600618	sh600636    氯碱化工   三爱富", 
"sz000738_sz000768":"sz000738	sz000768    中航动控   中航飞机", 
"sh600545_sz002302":"sh600545	sz002302    新疆城建   西部建设", 
"sh600089_sh601179":"sh600089	sh601179    特变电工 中国西电",  
'sh600501_sz002025':"sh600501   sz002025    航天晨光 航天电器",
'sh600108_sh601118':"sh600108   sh601118    亚盛集团 海南橡胶",
'sh600720_sz000789':"sh600720   sz000789    祁连山 万年青",
'sh600639_sh600648':"sh600639   sh600648    浦东金桥  外高桥",
'sh600831_sz000665':"sh600831   sz000665    广电网络 湖北广电",
'sh600216_sz002001':"sh600216	sz002001	浙江医药	新和成",
'sz000333_sz000651':"sz000333   sz000651    美的集团    格力电器",
'sz002136_sz002601':"sz002136	sz002601	安纳达	佰利联",
'sh600209_sz000735':"sh600209	sz000735	罗顿发展	罗牛山",
'sh600389_sh600596':"sh600389	sh600596	江山股份	新安股份",
'sz002441_sz300068':"sz002441	sz300068	众业达	南都电源",
'sh600884_sz002091':"sh600884	sz002091	杉杉股份	江苏国泰",
'sh600880_sz300052':"sh600880	sz300052	博瑞传播	中青宝",
'sh600597_sh600887':"sh600597	sh600887	光明乳业	伊利股份",
'sh600435_sh600501':"sh600435	sh600501	北方导航	航天晨光",
'sh600031_sz000157':"sh600031	sz000157	三一重工	中联重科",
'sh600343_sh600879':"sh600343	sh600879	航天动力	航天电子",
'sz000568_sz000858':"sz000568	sz000858	泸州老窖	五粮液",
'sz002279_sz002474':"sz002279	sz002474	久其软件	榕基软件",
'sh600030_sh600837':"sh600030	sh600837	中信证券	海通证券",
'sh601601_sh601628':"sh601601	sh601628	中国太保	中国人寿",
'sz000789_sz002233':"sz000789	sz002233	万年青	塔牌集团",
'sz000877_sh600425':"sz000877	sh600425	天山股份	青松建化",
'sz000001_sh601166':"sz000001	sh601166	平安银行	兴业银行",
'sh600011_sh600027':"sh600011	sh600027	华能国际	华电国际",
'sz000758_sh601168':"sz000758	sh601168	中色股份	西部矿业",
'sz000088_sz000507':"sz000088	sz000507	盐	田	港	珠海港			",
'sh600875_sh601727':"sh600875	sh601727	东方电气	上海电气	",
'sh600199_sh600702':"sh600199	sh600702	金种子酒	沱牌舍得	",
'sh600259_sz000831':"sh600259	sz000831	广晟有色	五矿稀土	",
'sh600026_sh601866':"sh600026	sh601866	中海发展	中海集运	",
'sh600789_sz002166':"sh600789	sz002166	鲁抗医药	莱茵生物	",
'sh600648_sh600663':"sh600648	sh600663	外高桥	陆家嘴",
'sh601801_sh601928':"sh601801	sh601928	皖新传媒	凤凰传媒",
'sh600048_sz000024':"sh600048	sz000024	保利地产	招商地产",
'sz002315_sh600831':"sz002315   sh600831    焦点科技    广电网络",
'sz002649_sz300079':"sz002649   sz300079    博彦科技    数码视讯",
}

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
    reconnect_database(dbconf.dbconf)
    g_cursor.execute("SELECT tag FROM dolphin_notificationnews WHERE pairid=%s and date=%s and tag = 1", (pairid, today_date))
    r = g_cursor.fetchall()
    if len(r) > 0 and int(r[0][0]) == 1:
        return True
    else:
        return False


''' store some information to database '''
def store_to_database(category, message):
    try:
        if category == 'delta_info':
            message = message.replace('None', '0.0')
        message = message.split("", 1)[1]
        items = tuple(message.split('\t'))
        placeholder = ', '.join(['%s']*len(items))
        if category == 'delta_info':
            fields = 'pairid, timestamp, minutes_to_closemarket, delta1, delta2'
            #sql = 'INSERT INTO dolphin_pairdelta (' + fields + ') VALUES (' + placeholder + ')' + str(items)
            #print >> open("/tmp/OnesideDolphin/errorlog", "a"), sql
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
                #log("debug", "update dolphin_asset: total(before)=%s, profit=%s, total(after)=%s" % (str(total), str(items[2]), str(items[3])))
            g_cursor.execute('INSERT INTO dolphin_asset (' + fields + ') VALUES (' + placeholder + ')', items)
                
        elif category == 'news_info':
            fields = 'pairid, date, news, tag'
            g_cursor.execute('INSERT INTO dolphin_notificationnews (' + fields + ') VALUES (' + placeholder + ')', items)
        g_conn.commit()
    except:
        err = traceback.format_exc()
        print >> sys.stderr, err
        print >> open("/tmp/OnesideDolphin/errorlog", "a"), err


#''' init logging '''
#def init_logging(pairid):
#    logger_name = pairid
#    logger = logging.getLogger(logger_name)
#    logger.setLevel(logging.DEBUG)
#    logger.propagate = False # its parent will not print log (especially when client use a 'root' logger)
#
#    fh = logging.FileHandler('dolphin/log/' + logger_name)
#    fh.setLevel(logging.DEBUG)
#    formatter = logging.Formatter("%(asctime)-15s %(levelname)s %(filename)s:%(lineno)s %(message)s")
#    fh.setFormatter(formatter)
#    logger.addHandler(fh)
#    global g_logger
#    g_logger = logger
#
#''' log message '''
#def log(category, message):
#    message = str(message)
#
#    if g_logger is not None:
#        if category.find('info') != -1:
#            g_logger.info(message)
#        elif category.find('warning') != -1:
#            g_logger.warning(message)
#        elif category.find('debug') != -1:
#            g_logger.debug(message)
#        elif category.find('error') != -1:
#            g_logger.error(message)
#    
#    if g_if_store2database:
#        store_to_database(category, message)

##################################################################
''' Useful functions to wait when market is closed '''

def if_close_market_today(today_date):
    a = [int(i) for i in today_date.split('-')]
    weekday = datetime.datetime(a[0], a[1], a[2]).weekday()
    if weekday == 5 or weekday == 6:
        #log('close_info', today_date + ' is weekend!')
        return True
#    reconnect_database()
    g_cursor.execute("select date from dolphin_marketclosedate where date>=%s", (today_date,))
    close_date_list = g_cursor.fetchall()
    close_date_list = [ str(i[0]) for i in close_date_list ]
    if today_date in close_date_list:
        #log('close_info', today_date + ' is in close date list!')
        return True
        
    return False

def wait_for_next_open(log):
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


def wait_for_half_open(log):
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
def update_asset(pairid, today_date, profit_by_delta, log):
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
    #print get_minutes_to_closemarket('15:01:00')
    print if_has_big_news("sh600048_sz000024", "2015-04-24")


