#coding: utf8
import datetime
import time
import os

pos_dir = "/tmp/OnesideDolphin/YesterdayPosition/"
now = datetime.datetime.now()

for f in os.listdir(pos_dir):
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(pos_dir + f))
    delta = now - mtime
    if delta.seconds < 45:
        print "warning!!!", f, delta.seconds
        
