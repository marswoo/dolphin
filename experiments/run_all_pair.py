#coding: utf8
import sys
import os
import re
import datetime
from dolphin.Util import candidate_stock_pairs as pairs

beg = sys.argv[1]
end = sys.argv[2]
tag = sys.argv[3]

dir = "result/run_all_pair."+beg.replace("-","") + "-"+ end.replace("-", "") + "." + tag
if sys.argv.count("f") != 0:
    os.system("rm -rf " + dir)
    os.system("rm -rf result/log." + tag)
    print "dir %s deleted." % dir
    print "dir result/log deleted."
os.system("mkdir -p " + dir)
os.system("mkdir -p dolphin/log")
os.system("mkdir -p result/log." + tag)

for pair in pairs:
    #if pair != "sz002279_sz002474":
    #    continue
    print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "--- processing %s." % pair
    print >> open(dir + "/" + "exp_"  + pair, "w"), os.popen("python strategy_comparator.py " + pair + " " + beg + " " + end).read()

output = open(dir + "/result", "w")
output_data = []
output_data.append("{0:20s}\t{1:10s}\t{2:20s}\t{3:20s}".format("pairid", "date", "test_stra_prof", "org_stra_prof", "offset"))
res = [0.0] * 2

for f in os.listdir(dir):
    data = [i for i in open(dir + "/" + f).read().split("\n") if i != ""]
    for line in data:
        tmp = line.split()
        if len(tmp) != 3:
            continue
        if tmp[1] != tmp[2] and re.match("^\d", tmp[0]) is not None: #两种策略的结果不相同，并且是日期
            output_data.append("{0:20s}\t{1:10s}\t{2:20s}\t{3:20s}\t{4:20s}".format(f.strip("exp_"), tmp[0], tmp[1], tmp[2], str(float(tmp[1]) - float(tmp[2]))))
            res[0] += float(tmp[1])
            res[1] += float(tmp[2])

output_data.append("\n{0:20s}\t{1:20s}".format("test_stra_prof_sum", "org_stra_prof_sum"))
output_data.append("{0:20s}\t{1:20s}".format(str(res[0]), str(res[1])))
for line in output_data:
    if line.strip() != "":
        print >> output, line

os.system("mv dolphin/log/Exp* result/log." + tag)
