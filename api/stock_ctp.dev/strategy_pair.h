#ifndef _STRATEGY_H__
#define _STRATEGY_H__

#include <string>
#include <map>
#include <iostream>
#include <algorithm>
#include <cmath>
#include <stdlib.h>

#include "ThostFtdcMdApiSSE.h"
#include "ThostFtdcUserApiStructSSE.h"

#include "datafeeder.h"
#include "observer.h"
#include "trader.h"
#include "util.h"

using namespace std;

class StrategyPair : public Observer
{
public:
    StrategyPair(const string& stock_pair, DataFeeder* df)
    {
        this->df = df;
        this->stock_pair = stock_pair;
        vector<string> stockids;
        Util::split(stock_pair, "_", stockids);
        if (stockids.size() != 2){
            cerr << "Stockids format ERROR in StrategyPair!" << endl;
        }
        stock_id1 = stockids[0];
        stock_id2 = stockids[1];
        stock_data[stock_id1] = map<string, float>();
        stock_data[stock_id2] = map<string, float>();

        max_delta_of_today = new vector<float>(2, -0.1);
        min_delta_of_today = new vector<float>(2, -0.1);
        min_span_delta_of_today = new vector<float>(2, 1.0);
        current_delta_relative_prices = new vector<float>(2, 0.0);
        current_stock_delta = new vector<float>(2, 0.0);
        last_stock_delta = new vector<float>(2, 0.0);
        buy_info1 = new vector<pair<float, int> >();
        buy_info2 = new vector<pair<float, int> >();
        sell_info1 = new vector<pair<float, int> >();
        sell_info2 = new vector<pair<float, int> >();

        minutes_to_closemarket = 241;
        expense_each_deal = 20000.0;
        if_enter_triggered = false;
        stop_buy_flag = false;
        want_sell_stock_enter_price = -1.0;
        want_sell_stock_amount = 0;
        want_sell_index = -1;
        base_enter_threshold = 0.013;

        mean_buy_price.push_back(0);
        mean_buy_price.push_back(0);
        mean_sell_price.push_back(0);
        mean_sell_price.push_back(0);
    }

    ~StrategyPair()
    {
    }

    void update(const string& stock_data_str, Trader* trader);

    string get_stock_id(int index)
    {
        if (0 == index) return stock_id1;
        if (1 == index) return stock_id2;
        cerr << ">>> Index ERROR in get_stock_id." << endl;
        return "";
    }

    int get_stock_index(const string& stockid)
    {
        if (stockid == stock_id1) return 0;
        if (stockid == stock_id2) return 1;
        cerr << ">>> Index ERROR in get_stock_id." << endl;
        return -1;
    }

private:
    Util util;
    DataFeeder* df;

    map<string, map<string, float> > stock_data;

    string today_bought_stock;
    string stock_id1;
    string stock_id2;
    string stock_pair;

    vector<float>* max_delta_of_today;
    vector<float>* min_delta_of_today;
    vector<float>* min_span_delta_of_today;
    vector<float>* current_delta_relative_prices;
    vector<float>* current_stock_delta;
    vector<float>* last_stock_delta;

    //two items: stock1 price, stock2 price
    vector<float> mean_buy_price;
    vector<float> mean_sell_price;

    vector<pair<float, int> >* buy_info1;
    vector<pair<float, int> >* buy_info2;
    vector<pair<float, int> >* sell_info1;
    vector<pair<float, int> >* sell_info2;

    float today_buy_price;
    float want_sell_stock_enter_price;
    float profit;
    float minutes_to_closemarket;
    float expense_each_deal;
    float base_enter_threshold;

    int today_buy_amout;
    int want_sell_stock_amount;
    int want_sell_index;

    bool if_enter_triggered;
    bool stop_buy_flag;

    string want_sell_stockid;

private:
    float get_delta_threshold_of_entering_market();

    bool if_enter_market(int stock_index);
    bool if_leave_time_right();

    void run();
    void close_today();
    void clear_yesterday_position();
    void trigger_buy(int stock_id);
    void check_stop_buy();

private:
    bool check_and_parse(vector<string>& tmp_v, map<string, map<string, float> > &stock_data);
    void get_buy_info(string& current_stockid);
    void get_sell_info(string& current_stockid);
};

#endif /* end of include guard: _STRATEGY_H__ */

