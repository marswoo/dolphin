#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText

class NeteaseMail:
    def __init__(self):
        self.user = 'woody213'
        self.fromaddr = self.user + '@yeah.com'
        self.password = 'iamwhoiam126'

    def send_mail(self, to_list, subject, content):
        '''
        to_list:发给谁
        sub:主题
        content:内容
        send_mail("aaa@126.com","subject","content")
        '''
        me = self.user + "<" + self.fromaddr + ">"
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = self.fromaddr
        msg['To'] = ";".join(to_list)
        try:
            session = smtplib.SMTP('smtp.126.com')
            session.login(self.fromaddr, self.password)
            session.sendmail(me, to_list, msg.as_string())
            session.close()
            return True
        except Exception, e:
            print str(e)
            return False


import urllib2, datetime, sys
from bs4 import BeautifulSoup
from conf.dbconf import dbconf
import Util
import re
import os

if __name__ == '__main__':
    stock_pairs = Util.candidate_stock_pairs
    keywords = ['中报', '季报', '年报', '停牌']

    mail_content = ''
    today_date = str(datetime.date.today())
    tomorrow_date = str(datetime.date.today() + datetime.timedelta(days = 1))
    yesterday_date = str(datetime.date.today() + datetime.timedelta(days = -1))
    Util.reconnect_database(dbconf)

    print 'Get shock news on ', today_date
    for pair in stock_pairs:
        for stockid in pair.split('_'):
            flag = "0"
            db_content = ''
            #url = 'http://money.finance.sina.com.cn/corp/view/vCB_AllMemordDetail.php?stockid='+stockid[2:]
            url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/%s.phtml' % stockid
            #print url
            html = urllib2.urlopen(url).read()
            soup = BeautifulSoup(html)
            raw_date_str = str(soup.find(id="con02-7").find_all("ul"))
            date_list = []
            for i in re.split("[<a|<br>]", raw_date_str):
                if i.count("2015-") != 0:
                    date_list.append(i.strip()[8:-11])

            a = soup.find(id="con02-7").find_all('a')
            index = 0
            for i in a:
                index += 1
                title_text = i.text.encode("utf8")
                if title_text.count("下一页") != 0 or len(date_list) == 0:
                    break
                news_date = date_list.pop(0)
                mail_content_tmp = stockid + " " + news_date + " " + title_text
                if news_date in [today_date, tomorrow_date]:
                    for k in keywords:
                        if mail_content_tmp.count(k) != 0:
                            mail_content += (mail_content_tmp + '\n***************************\n')
                            db_content += (mail_content_tmp + '\n***************************\n')
                            flag = "1"
            Util.log('news_info', '\t'.join([ pair, today_date, db_content, str(flag) ]))

    print mail_content
    if flag == "1":
        mail = NeteaseMail()
        mail.send_mail(self, "woody213@yeah.net,80382133@qq.com", "big news", mail_content)
        #print os.popen("echo \"%s\" | mail -s \"big news!!\" woody213@yeah.net,80382133@qq.com" % mail_content).read()


