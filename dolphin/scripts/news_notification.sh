set -eux

/root/usr/bin/python news_notification.py &> /dev/null
date=`date +"%Y%m%d"`
mkdir -p "/root/mail_notify/task/dolphin/data_processor/data/"$date
cp /root/framework.online/common_log/news_notification.log.`date +"%Y-%m-%d"` /root/mail_notify/task/dolphin/data_processor/data/$date/stock_bignews.data.tmp
python ~/framework.online/dolphin/scripts/strip_file.py /root/mail_notify/task/dolphin/data_processor/data/$date/stock_bignews.data.tmp > /root/mail_notify/task/dolphin/data_processor/data/$date/stock_bignews.data
cd /root/mail_notify/task/dolphin/ && sh send_mail.sh -vt `date +"%Y%m%d"`
