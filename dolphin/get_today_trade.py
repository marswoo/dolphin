#coding: utf8
import os
import datetime
from conf.dbconf import dbconf
import MySQLdb
from warnings import filterwarnings
from collections import defaultdict
import sys

pair_name_map = { 
    'sh600216_sz002001': "浙江医药_新和成股",    # 医药
    'sh601801_sh601999': "皖新传媒_出版传媒",    # 传媒
    'sz002136_sz002601': "安纳达股_佰利联股",    # 钛白粉
    'sh600209_sz000735': "罗顿发展_罗牛山股",    # 海南旅游岛
    'sh600389_sh600596': "江山股份_新安股份",    # 金改
    'sz002441_sz300068': "众业达股_南都电源",    # 电气设备
    'sh600017_sh601880': "日照港股_大连港股",    # 港口
    'sh600884_sz002091': "杉杉股份_江苏国泰",    # 动力锂电池
    'sz000758_sz000993': "中色股份_闽东电力",    # 稀土
    'sh600880_sz300052': "博瑞传播_中青宝股",    # 手机游戏
    'sh600597_sh600887': "光明乳业_伊利股份",    # 乳业
    'sh600789_sz002166': "鲁抗医药_莱茵生物",    # 生物制药
    'sh600435_sh600501': "北方导航_航天晨光",    # 航天军工
    'sh600639_sh600663': "浦东金桥_陆家嘴股",    # 园区开发
    'sh600391_sz000561': "成发科技_烽火电子",    # 航天军工
    'sh600031_sz000157': "三一重工_中联重科",
    'sh600999_sh601788': "招商证券_光大证券",
    'sz300042_sz300270': "朗科科技_中威电子",
    'sh600410_sz002544': "华胜天成_杰赛科技",
    'sz002031_sz300193': "巨轮股份_佳士科技",
    'sh600343_sh600879': "航天动力_航天电子",
    'sz000568_sz000858': "泸州老窖_五粮液股",
    'sz002279_sz002474': "久其软件_榕基软件",
}

id_name_map = defaultdict(str)
id_pair_map = defaultdict(str)
for key in pair_name_map:
    id1, id2 = key.split("_")
    name1, name2 = pair_name_map[key].split("_")
    id_name_map[id1] = name1
    id_name_map[id2] = name2
    id_pair_map[id1] = key
    id_pair_map[id2] = key

today = datetime.datetime.now().strftime("%Y-%m-%d")
if len(sys.argv) == 2:
    today = sys.argv[1]
    print "date: ", today

g_conn = MySQLdb.connect(host = dbconf['HOST'], user = dbconf['USER'], passwd = dbconf['PASSWORD'], db = dbconf['NAME'], charset = 'utf8')
g_conn.autocommit(True)
g_cursor = g_conn.cursor()
filterwarnings('ignore', category = MySQLdb.Warning)
g_cursor.execute("select * from dolphin_deal where timestamp > '" + today + "'")

#-----------------------------------------output
title = "{0:15s}{1:15s}{7:25s}{2:15}{3:15s}{4:10.3s}{5:10s}{6:>20s}".format('time', 'id', 'name', 'action', 'price', 'amount', 'real', 'pair')
print title
print '-'*len(title)
trade_real = []
for i in g_cursor.fetchall():
    time = i[1].strftime("%Y%m%d")
    action = i[2]
    if action == 0:
        action = "buy"
    else:
        action = "sell"
    id = i[3]
    name = id_name_map[id]
    price = i[4]
    amount = i[5]
    real = i[6]
    pair = id_pair_map[id]
    if real == 0:
        real = "false"
    else:
        real = "true"

    #real data
    if real == "true":
        trade_real.append([time, id, name, action, price, amount, real, pair])
    else:
        print "{0:15s}{1:15s}{7:25s}{2:15}{3:15s}{4:10.3f}{5:10d}{6:>20s}".format(time, id, name, action, price, amount, real, pair)

print
print title
print '-'*len(title)
trade_real = sorted(trade_real, key=lambda p: p[3])
for i in trade_real:
    print >> sys.stderr, "{0:15s}{1:15s}{7:25s}{2:15}{3:15s}{4:10.3f}{5:10d}{6:>20s}".format(*i)

g_cursor.close()
g_conn.close()
