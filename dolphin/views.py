from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from dolphin.models import PairDelta, Deal, Asset, StockMetaData, MarketCloseDate
#from django.utils import simplejson
import json as simplejson
from django.db.models import Q
import shlex, subprocess, datetime, time, sys, pickle, os
from django.core.serializers.json import DjangoJSONEncoder

from dolphin.CTPStockDataFeeder import CTPL2StockDataFeeder
from dolphin.StockDataFeeder import StockSinaRealDataFeeder
from dolphin.CTPHBAccount import CTPHBAccount
from dolphin.Util import candidate_stock_pairs

stock_pairs = candidate_stock_pairs

stock_datafeeder = None
account = None

def init(request):
    global stock_datafeeder
    if stock_datafeeder:
        del stock_datafeeder
    stock_datafeeder = CTPL2StockDataFeeder()
    print "stock_datafeeder ready"

    global account
    if account:
        del account
    account = CTPHBAccount()
    time.sleep(2)
    account.update_account_info()
    time.sleep(2)
    print "account ready"
    return HttpResponse('Init Success!')

def check_init():
    global stock_datafeeder
    if not stock_datafeeder:
        stock_datafeeder = CTPL2StockDataFeeder()
        print "stock_datafeeder check_init"
        time.sleep(2)

    global account
    if not account:
        account = CTPHBAccount()
        time.sleep(2)
        account.update_account_info()
        time.sleep(2)
        print "account check_init"

def get_stockdata(request, stockid):
    check_init()
    rr = stock_datafeeder.get_data(str(stockid))
    return HttpResponse(rr)

def clear(request, pair):
    sina_datafeeder = StockSinaRealDataFeeder()
    account.update_account_info()
    time.sleep(5)
    position_info = account.get_account_info()['stocklist']
    for stockid in pair.split('_'):
        stock_info = sina_datafeeder.get_data(str(stockid))
        price = stock_info['buy_1_price'] - 0.03
        amount = 0
        if stockid in position_info.keys():
            amount = position_info[stockid]
        account.sell( str(stockid), [(price, amount)] )

    return HttpResponse('Clear pair '+pair+' success!')


def trade(request, functionid):
    global account
    if not account:
        account = CTPHBAccount()
        time.sleep(2)
    if functionid == 'get_account_info':
        return HttpResponse( str(account.get_account_info()) )
    elif functionid == 'update_account_info':
        return HttpResponse( str(account.update_account_info()) )
    elif functionid == 'get_today_trades':
        return HttpResponse( str(account.get_today_trades()) )
    elif functionid == 'update_today_trades':
        return HttpResponse( str(account.update_today_trades()) )
    elif functionid.startswith('buy'):
        items = functionid.split('_')
        if len(items) != 4:
            return HttpResponse( 'Error url' )
        return HttpResponse( str(account.buy(str(items[1]), [(float(items[2]), int(items[3]))])) )
    elif functionid.startswith('sell'):
        items = functionid.split('_')
        if len(items) != 4:
            return HttpResponse( 'Error url' )
        return HttpResponse( str(account.sell(str(items[1]), [(float(items[2]), int(items[3]))])) )
        


############################################################################

def index(request):
    pair_status = get_pair_status()
    return render(request, 'dolphin/index.html',
                {
                    'pair_status': pair_status,
                    'today_date': datetime.date.today(),
                })

def get_pair_status():
    pair_status = {}
    args = shlex.split("ps aux")
    ps = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
    processes = ps.split('\n')
    for pair in stock_pairs:
        pair_status[pair] = False
        for row in processes:
            if row.find('run_') != -1 and row.find(pair) != -1:
                pair_status[pair] = True

    return pair_status

def start_pair(pair):
    for stockid in pair.split('_'):
        stock_datafeeder.subscribe(str(stockid))
    cmd = 'python dolphin/oneside_run_real.py ' + pair
    cmd = cmd.encode('ascii')
    args = shlex.split(cmd)
    subprocess.Popen(args)

def stop_pair(pair):
    args = shlex.split("ps aux")
    ps = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
    processes = ps.split('\n')
    for row in processes:
        if row.find(pair) != -1 and row.find('run_') != -1:
            subprocess.call(['kill', '-9', row.split()[1]])

def start(request, pair):
    check_init()
    pair_status = get_pair_status()
    if not pair_status[pair]:
        start_pair(pair)
    return HttpResponseRedirect('/dolphin')

def stop(request, pair):
    stop_pair(pair)
    return HttpResponseRedirect('/dolphin')
        
def start_all(request):
    pair_status = get_pair_status()
    for pair in stock_pairs:
        if not pair_status[pair]:
            start_pair(pair)
    return HttpResponseRedirect('/dolphin')

def stop_all(request):
    for pair in stock_pairs:
        stop_pair(pair)
    return HttpResponseRedirect('/dolphin')
   

def detail(request, pair, date):
    pair_status = get_pair_status()
    date = date.split('-')
    date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
    deltas = PairDelta.objects.filter(pairid=pair, timestamp__startswith=date)
    stockids = pair.split('_')
    deals = Deal.objects.filter(Q(stockid=stockids[0]) | Q(stockid=stockids[1]), timestamp__startswith=date).order_by('timestamp')
    deals = sorted(deals, key=lambda s:s.stockid)
    two_deal_times = [ time.mktime(deal.timestamp.timetuple())*1000 for deal in deals]
    if len(two_deal_times) >= 3:
        two_deal_times = [ two_deal_times[0], two_deal_times[2] ]
    if not os.path.isdir("/tmp/OnesideDolphin/view_detail/"):
        os.system("mkdir -p /tmp/OnesideDolphin/view_detail/")

    deltas_positive_file = "/tmp/OnesideDolphin/view_detail/" + pair + "_deltas_positive"
    if os.path.exists(deltas_positive_file):
        deltas_positive = pickle.load(open(deltas_positive_file, "rb"))
    else:
        deltas_positive = [ [time.mktime(delta.timestamp.timetuple())*1000, float(delta.delta1)] for delta in deltas ]
        pickle.dump(deltas_positive, open(deltas_positive_file, "wb"))
        
    deltas_negative_file = "/tmp/OnesideDolphin/view_detail/" + pair + "_deltas_negative"
    if os.path.exists(deltas_negative_file):
        deltas_negative = pickle.load(open(deltas_negative_file, "rb"))
    else:
        deltas_negative = [ [time.mktime(delta.timestamp.timetuple())*1000, float(delta.delta2)] for delta in deltas ]
        pickle.dump(deltas_negative, open(deltas_negative_file, "wb"))

    metadata1 = StockMetaData.objects.filter(stockid=stockids[0], date=date)
    metadata2 = StockMetaData.objects.filter(stockid=stockids[1], date=date)
    stock_metadatas_1_file = "/tmp/OnesideDolphin/view_detail/" + pair + "_stock_metadatas_1"
    if os.path.exists(stock_metadatas_1_file):
        stock_metadatas_1 = pickle.load(open(stock_metadatas_1_file, "rb"))
    else:
        stock_metadatas_1 = [ [time.mktime( time.strptime(str(date)+' '+str(d.time), '%Y-%m-%d %H:%M:%S') )*1000, float((d.current_price-d.yesterday_close_price)/d.yesterday_close_price) ] for d in metadata1 ]
        pickle.dump(stock_metadatas_1, open(stock_metadatas_1_file, "wb"))

    stock_metadatas_2_file = "/tmp/OnesideDolphin/view_detail/" + pair + "_stock_metadatas_2"
    if os.path.exists(stock_metadatas_2_file):
        stock_metadatas_2 = pickle.load(open(stock_metadatas_2_file, "rb"))
    else:
        stock_metadatas_2 = [ [time.mktime( time.strptime(str(date)+' '+str(d.time), '%Y-%m-%d %H:%M:%S') )*1000, float((d.current_price-d.yesterday_close_price)/d.yesterday_close_price) ] for d in metadata2 ]
        pickle.dump(stock_metadatas_2, open(stock_metadatas_2_file, "wb"))


    return render(request, 'dolphin/detail.html', 
            {'pair_status': pair_status,
             'today_date': datetime.date.today(),
             'deltas_positive': simplejson.dumps(deltas_positive, cls=DjangoJSONEncoder),
             'deltas_negative': simplejson.dumps(deltas_negative, cls=DjangoJSONEncoder),
             'two_deal_times' : simplejson.dumps(two_deal_times),
             'deals': deals,
             'stock_metadatas_1': simplejson.dumps(stock_metadatas_1, cls=DjangoJSONEncoder),
             'stock_metadatas_2': simplejson.dumps(stock_metadatas_2, cls=DjangoJSONEncoder),
             'stockids': simplejson.dumps(stockids),
            } )

def view_assets(request): 
    pair_status = get_pair_status()
    pairid = stock_pairs[0]
    assets = Asset.objects.all()
    assets = [ [time.mktime(asset.date.timetuple())*1000, asset.total] for asset in assets ]
    return render(request, 'dolphin/assets.html',
            {'pair_status': pair_status,
             'today_date': datetime.date.today(),
             'assets': simplejson.dumps(assets),
            })

