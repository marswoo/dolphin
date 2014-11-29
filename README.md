#CONFIGURATION

---

1. pre-installs:
    1. install python2.7.8
    1. yum install mysql-server
    1. install python-pip
    1. install Django #pip search Django==1.7
    1. install MySQL-python #https://pypi.python.org/pypi/MySQL-python/1.2.5
    1. install pip https://pypi.python.org/packages/source/p/pip/pip-1.5.6.tar.gz#md5=01026f87978932060cc86c1dc527903e
    1. yum install python-devel
    1. install PIL http://effbot.org/downloads/Imaging-1.1.7.tar.gz
    1. pip install simplejson beautifulsoup4
    1. yum install libjpeg-devel.i386; http://www.kodkast.com/linux-package-installation-steps?pkg=libjpeg-devel.i386
    1. install libjpeg8, ftp://195.220.108.108/linux/opensuse/ports/ppc/distribution/12.2/repo/oss/suse/ppc/libjpeg8-8.3.0-12.1.13.ppc.rpm
    1. sudo apt-get install libmysqlclient-dev; # or yum install mysql-dev1.

1. config
    1. service mysqld start
    1. git submodule init; git submodule update
    1. mysql -uroot -e "create database tf2;"
    1. python manage.py syncdb
    1. insert 2 rows into table dolphin_asset if it's empty

1. env config
    1. modify /etc/mysql/my.cnf::bind_address to local ip address
    1. export LD_LIBRARY_PATH="$HOME/programs/lib/python2.7/site-packages/pzyctp:$LD_LIBRARY_PATH"


