#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2, datetime, sys
from bs4 import BeautifulSoup
from conf.dbconf import dbconf
import os
import re
import Util
import os

if __name__ == '__main__':
    logname= "/root/framework.online/common_log/news_notification.log." + str(datetime.date.today())
    log = open("/root/framework.online/common_log/news_notification.log." + str(datetime.date.today()), "w")
    log_norm = open("/root/framework.online/common_log/news_notification.normlog." + str(datetime.date.today()), "w")
    stock_pairs = Util.candidate_stock_pairs
    keywords = ['中报', '季报', '年报', '停牌', '业绩', '快报', '重组', '利润']

    mail_content = ''
    today_date = str(datetime.date.today())
    tomorrow_date = str(datetime.date.today() + datetime.timedelta(days = 1))
    yesterday_date = str(datetime.date.today() + datetime.timedelta(days = -1))
    Util.reconnect_database(dbconf)

    print 'Get shock news on ', today_date
    for pair in stock_pairs:
        #if pair != "sz000333_sz000651":
        #    continue
        for stockid in pair.split('_'):
            flag = "0"
            db_content = ''
            url1 = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/%s.phtml' % stockid
            url2 = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllBulletin/stockid/%s.phtml' % stockid[2:]
            for url in [url1, url2]:
                try:
                    html = urllib2.urlopen(url).read().decode('gb2312').encode('utf8')
                except:
                    html = urllib2.urlopen(url).read()
                soup = BeautifulSoup(html)
                raw_date_str = str(soup.find(id="con02-7").find_all("ul"))
                date_list = []
                year = str(datetime.date.today().year)
                for i in re.split("[<a|<br>]", raw_date_str):
                    if i.count(year + "-") != 0:
                        date_list.append(i.strip())

                a = soup.find(id="con02-7").find_all('a')
                index = 0
                for i in a:
                    index += 1
                    title_text = i.text.encode("utf8")
                    if title_text.count("下一页") != 0 or len(date_list) == 0:
                        break
                    try:
                        news_date = re.compile("\d\d\d\d-\d\d-\d\d").search(date_list.pop(0)).group(0)
                    except:
                        continue
                    mail_content_tmp = "".join((stockid, news_date, title_text))
                    #print title_text+""+news_date
                    print >> log_norm, title_text
                    if news_date in [yesterday_date, today_date, tomorrow_date]:
                        for k in keywords:
                            if mail_content_tmp.count(k) != 0:
                                mail_content += mail_content_tmp + "\n"
                                db_content += (mail_content_tmp + '\n***************************\n')
                                flag = "1"
                Util.store_to_database('news_info', ''+'\t'.join([ pair, today_date, db_content, str(flag) ]))

    mail_content = mail_content.strip("\n").strip()
    mail_content = "\t".join(mail_content.split(""))
    print >> log, mail_content
    os.system("find /root/framework.online/common_log -mtime +10 | xargs rm -f")
