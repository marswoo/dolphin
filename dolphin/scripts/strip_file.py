import sys

data = open(sys.argv[1]).read().strip("\n")
for i in data.split("\n"):
    if i.strip() == "":
        continue
    print i.strip()
print "end_stockid	end_date	end_title"
