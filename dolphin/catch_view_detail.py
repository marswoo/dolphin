from Util import candidate_stock_pairs
import datetime, os, time
date = datetime.datetime.now().strftime("%Y-%m-%d")
for pair in candidate_stock_pairs:
    cmd = "curl http://localhost:8082/dolphin/detail/" + pair + "/" + date + "/ &> /dev/null"
    time.sleep(1)
    os.system(cmd)
    cmd = "find /tmp/OnesideDolphin/view_detail -mtime +30 | xargs rm -rf"
    os.system(cmd)

