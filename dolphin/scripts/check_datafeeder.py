#coding: utf8
import datetime
import time
import os
from Util import *
import MySQLdb
from conf.dbconf import dbconf


pos_dir = "/tmp/OnesideDolphin/YesterdayPosition/"
now = datetime.datetime.now()
min_2_close = get_minutes_to_closemarket(now.strftime("%H:%M:%S"))

if min_2_close != -1 and min_2_close < 241 and min_2_close != 120.5:
    #避免一开始就触发
    if min_2_close > 239:
        exit(0)
    elif min_2_close < 121 and min_2_close > 118:
        exit(0)

    g_conn = MySQLdb.connect(host = dbconf['HOST'], user = dbconf['USER'], passwd = dbconf['PASSWORD'], db = dbconf['NAME'], charset = 'utf8')
    g_cur = g_conn.cursor()

    stockid = candidate_stock_pairs[0].split("_")[0]

    sql = "select max(time) from dolphin_stockmetadata where date='" + str(now.date()) + "' and stockid='" + stockid + "'"
    g_cur.execute(sql)
    res = g_cur.fetchall()
    if len(res) > 0 and len(res[0]) > 0:
        data_up_time = res[0][0]
        up_time = now - now.replace(hour=0).replace(minute=0).replace(second=0)
        if data_up_time is None:
            seconds = 9999
        else:
            delta = up_time - data_up_time
            seconds = delta.days*24*3600 + delta.seconds

        if seconds > 40:
            print "warning!!!", seconds, datetime.datetime.now()
            if not os.path.exists("/tmp/check_datafeeder.flag"):
                #send email 
                os.popen("cd /root/mail_notify/src && python mail_simple.py 'woody213@yeah.net;80382133@qq.com' 'restart b/c datafeeder' 'rt'").read()
                os.system("touch /tmp/check_datafeeder.flag")
                os.system("cd /root/framework.online && sh kill.sh && sh run.sh")
                time.sleep(1)
                os.system("curl http://127.0.0.1:8082/dolphin/init/")
                time.sleep(20)
                rt = os.system("curl http://127.0.0.1:8082/dolphin/start_all/")
                if rt != 0:
                    os.system("curl http://127.0.0.1:8082/dolphin/start_all/")
                os.system("rm -f /tmp/check_datafeeder.flag")

    g_cur.close()
    g_conn.close()
