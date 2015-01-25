#coding: utf8
import sys
import os
import re
import datetime
from dolphin.Util import candidate_stock_pairs as pairs

beg = sys.argv[1]
end = sys.argv[2]

dir = "run_all_pair."+beg.replace("-","") + "-"+ end.replace("-", "")
if sys.argv.count("f") != 0:
    os.system("rm -rf " + dir)
    os.system("rm -rf log")
    print "dir %s deleted." % dir
    print "dir log deleted."
os.system("mkdir -p " + dir)
os.system("mkdir -p log")

for pair in pairs:
    print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "--- processing %s." % pair
    print >> open(dir + "/" + "exp_"  + pair, "w"), os.popen("python strategy_comparator.py " + pair + " " + beg + " " + end).read()

output = open(dir + "/result", "w")

for f in os.listdir(dir):
    data = [i for i in open(dir + "/" + f).read().split("\n") if i != ""]
    for line in data:
        tmp = line.split()
        if len(tmp) != 3:
            continue
        if tmp[1] != tmp[2] and re.match("^\d", tmp[0]) is not None: #两种策略的结果不相同，并且是日期
            print >> output, "{0:s}\t{1:s}\ttest_stra:{2:s}\torg_stra:{3:s}".format(f.strip("exp_"), tmp[0], tmp[1], tmp[2])
    print >> output, ""

os.system("mv dolphin/log/Exp* log/")
