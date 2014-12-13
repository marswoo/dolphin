#coding: utf8
import urllib2
data = urllib2.urlopen("http://www.marswoo.com:8082/dolphin/", timeout=5).read()
import datetime
from time import *
import time
now = strftime('%H:%M:%S', localtime())
from Util import *
status = get_minutes_to_closemarket(now)
import os
if status != -1 and status != 241 and status != 120.5 and data.count("idle") != 0:
    print os.popen("echo \"there\'s idle pair!\" | mail -s \"dolphin idle alert!\" woody213@yeah.net,80382133@qq.com").read()
    print "sent", status, data.count("idle")
else:
    print "np"
