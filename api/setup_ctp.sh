
if [ -d "./pzyctp" ] ; then
	rm -rf pzyctp
fi
if [ -d "/usr/lib/python2.6/site-packages/pzyctp" ] ; then
	rm -rf /usr/lib/python2.6/site-packages/pzyctp
fi

set -eux

mkdir pzyctp
cp __init__.py pzyctp/
cd stock_ctp && make
cd -

mkdir pzyctp/stock_ctp
cp stock_ctp/datafeeder.py 	pzyctp/stock_ctp/
cp stock_ctp/_datafeeder.so 	pzyctp/stock_ctp/
cp stock_ctp/trader.py 		pzyctp/stock_ctp/
cp stock_ctp/_trader.so 		pzyctp/stock_ctp/
cp stock_ctp/__init__.py 		pzyctp/stock_ctp/
cp stock_ctp/lib/th*.so 			pzyctp/stock_ctp/

mv pzyctp /usr/lib/python2.6/site-packages
[ ! -e /usr/lib/libthostmduserapiSSE.so ] && \
ln -s /usr/lib/python2.6/site-packages/pzyctp/stock_ctp/thostmduserapiSSE.so /usr/lib/libthostmduserapiSSE.so

[ ! -e /usr/lib/libthosttraderapiSSE.so ] && \
ln -s /usr/lib/python2.6/site-packages/pzyctp/stock_ctp/thosttraderapiSSE.so /usr/lib/libthosttraderapiSSE.so

[ ! -e /tmp/CTP_LTS_trade/ ] && \
mkdir /tmp/CTP_LTS_trade/

[ ! -e /tmp/CTP_LTS_data/ ] && \
mkdir /tmp/CTP_LTS_data/

exit 0
