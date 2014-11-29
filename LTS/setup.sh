
if [ -d "./pzyctp" ] ; then
	rm -rf pzyctp
fi
if [ -d "/usr/lib/python2.6/site-packages/pzyctp" ] ; then
	rm -rf /usr/lib/python2.6/site-packages/pzyctp
fi

set -eux

mkdir pzyctp
cp __init__.py pzyctp/
cd stock && make
cd -

LIST="stock"
for d in $LIST
do
	mkdir pzyctp/$d
	cp $d/datafeeder.py 	pzyctp/$d/
	cp $d/_datafeeder.so 	pzyctp/$d/
	cp $d/trader.py 		pzyctp/$d/
	cp $d/_trader.so 		pzyctp/$d/
	cp $d/__init__.py 		pzyctp/$d/
	cp $d/api/*.so 			pzyctp/$d/
done

mv pzyctp /usr/lib/python2.6/site-packages
[ ! -e /usr/lib/libsecuritymduserapi.so ] && ln -s /usr/lib/python2.6/site-packages/pzyctp/stock/libsecuritymduserapi.so /usr/lib/libsecuritymduserapi.so
[ ! -e /usr/lib/libsecuritytraderapi.so ] && ln -s /usr/lib/python2.6/site-packages/pzyctp/stock/libsecuritytraderapi.so /usr/lib/libsecuritytraderapi.so
[ ! -e /tmp/CTP_LTS_trade/ ] && mkdir /tmp/CTP_LTS_trade/
[ ! -e /tmp/CTP_LTS_data/ ] && mkdir /tmp/CTP_LTS_data/

exit 0
