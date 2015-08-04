echo "drop database if exists tf2_sample; create database tf2_sample;" | mysql -uroot
mysqldump -uroot tf2 --no-data > /tmp/mysql_structure_tmp
mysql -uroot tf2_sample < /tmp/mysql_structure_tmp
mysqldump -uroot tf2 dolphin_stockmetadata --where="DATE_FORMAT(concat(date, ' ', time), '%i') = 0" > /data/tmp/metadata
mysql -uroot tf2_sample < /data/tmp/metadata
