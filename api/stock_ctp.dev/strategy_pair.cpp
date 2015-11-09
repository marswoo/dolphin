#include <iostream>
#include "strategy_pair.h"

//check stock_data_str and parse to map
bool StrategyPair::check_and_parse(vector<string>& tmp_v, map<string, map<string, float> > &stock_data)
{
    if (22 > tmp_v.size() || 0 == atof(tmp_v[4].c_str()))
    {
        return false;
    }

    stock_data[tmp_v[0]]["current_price"] = atof(tmp_v[3].c_str());
    stock_data[tmp_v[0]]["yesterday_close_price"] = atof(tmp_v[4].c_str());
    stock_data[tmp_v[0]]["today_open_price"] = atof(tmp_v[5].c_str());
    stock_data[tmp_v[0]]["today_highest_price"] = atof(tmp_v[6].c_str());
    stock_data[tmp_v[0]]["today_lowest_price"] = atof(tmp_v[7].c_str());
    stock_data[tmp_v[0]]["volume"] = atof(tmp_v[8].c_str());
    stock_data[tmp_v[0]]["turnover"] = atof(tmp_v[9].c_str());
    stock_data[tmp_v[0]]["buy_1_price"] = atof(tmp_v[10].c_str());
    stock_data[tmp_v[0]]["buy_1_amount"] = atof(tmp_v[11].c_str());
    stock_data[tmp_v[0]]["buy_2_price"] = atof(tmp_v[12].c_str());
    stock_data[tmp_v[0]]["buy_2_amount"] = atof(tmp_v[13].c_str());
    stock_data[tmp_v[0]]["buy_3_price"] = atof(tmp_v[14].c_str());
    stock_data[tmp_v[0]]["buy_3_amount"] = atof(tmp_v[15].c_str());
    stock_data[tmp_v[0]]["sell_1_price"] = atof(tmp_v[16].c_str());
    stock_data[tmp_v[0]]["sell_1_amount"] = atof(tmp_v[17].c_str());
    stock_data[tmp_v[0]]["sell_2_price"] = atof(tmp_v[18].c_str());
    stock_data[tmp_v[0]]["sell_2_amount"] = atof(tmp_v[19].c_str());
    stock_data[tmp_v[0]]["sell_3_price"] = atof(tmp_v[20].c_str());
    stock_data[tmp_v[0]]["sell_3_amount"] = atof(tmp_v[21].c_str());

    return true;
}


//get actual buy price (mean)
//if limit up/down, mean_buy_price == -1 and buy_info is empty
void StrategyPair::get_buy_info(string& current_stockid)
{
    vector<pair<float, int> >* buy_info = NULL;
    if (0 == get_stock_index(current_stockid)) buy_info = buy_info1;
    if (1 == get_stock_index(current_stockid)) buy_info = buy_info2;
    if (NULL == buy_info)
        cerr << ">>> get_buy_info ERROR!" << endl;

    buy_info->clear();

    float total_cost = 0.0;

    int want_unit_amount = this->expense_each_deal / stock_data[current_stockid]["current_price"] / 100;
    int already_buy_unit_amount = 0;
    int has_unit_num = stock_data[current_stockid]["sell_1_amount"] / 100;
    int actual_buy_unit = min(has_unit_num, want_unit_amount-already_buy_unit_amount);

    already_buy_unit_amount += actual_buy_unit;
    total_cost += actual_buy_unit * stock_data[current_stockid]["sell_1_price"];
    buy_info->push_back(make_pair(stock_data[current_stockid]["sell_1_price"], (int)actual_buy_unit * 100));

    if (already_buy_unit_amount <= want_unit_amount){
        has_unit_num = stock_data[current_stockid]["sell_2_amount"] / 100;
        actual_buy_unit = min(has_unit_num, want_unit_amount-already_buy_unit_amount);
        already_buy_unit_amount += actual_buy_unit;
        total_cost += actual_buy_unit * stock_data[current_stockid]["sell_2_price"];
        buy_info->push_back(make_pair(stock_data[current_stockid]["sell_2_price"], (int)actual_buy_unit * 100));
    }
    
    if (already_buy_unit_amount <= want_unit_amount){
        has_unit_num = stock_data[current_stockid]["sell_3_amount"] / 100;
        actual_buy_unit = min(has_unit_num, want_unit_amount-already_buy_unit_amount);
        already_buy_unit_amount += actual_buy_unit;
        total_cost += actual_buy_unit * stock_data[current_stockid]["sell_3_price"];
        buy_info->push_back(make_pair(stock_data[current_stockid]["sell_3_price"], (int)actual_buy_unit * 100));
    }
    
    mean_buy_price[get_stock_index(current_stockid)] = -1;

    if (already_buy_unit_amount >= want_unit_amount && already_buy_unit_amount != 0)
    {
        mean_buy_price[get_stock_index(current_stockid)] = total_cost / already_buy_unit_amount;
    }
}


//get actual sell price (mean)
//if limit up/down, mean_sell_price == -1 and sell_info is empty
void StrategyPair::get_sell_info(string& current_stockid)
{
    vector<pair<float, int> >* sell_info = NULL;
    if (0 == get_stock_index(current_stockid)) sell_info = sell_info1;
    if (1 == get_stock_index(current_stockid)) sell_info = sell_info2;
    if (NULL == sell_info)
        cerr << ">>> get_sell_info ERROR!" << endl;

    sell_info->clear();

    int already_own_unit_amount = 0;
    int want_unit_amount = 0;

    if (this->want_sell_stockid == current_stockid)
    {
        already_own_unit_amount = this->want_sell_stock_amount / 100;
    }

    if (0 != already_own_unit_amount)
    {
        want_unit_amount = already_own_unit_amount;
    }

    float total_cost = 0.0;

    int already_sell_unit_amount = 0.0;
    int has_unit_num = stock_data[current_stockid]["buy_1_amount"] / 100;
    int actual_sell_unit = min(has_unit_num, want_unit_amount-already_sell_unit_amount);

    already_sell_unit_amount += actual_sell_unit;
    total_cost += actual_sell_unit * stock_data[current_stockid]["buy_1_price"];
    sell_info->push_back(make_pair(stock_data[current_stockid]["buy_1_price"], (int)actual_sell_unit * 100));

    if (already_sell_unit_amount <= want_unit_amount){
        has_unit_num = stock_data[current_stockid]["buy_2_amount"] / 100;
        actual_sell_unit = min(has_unit_num, want_unit_amount-already_sell_unit_amount);
        already_sell_unit_amount += actual_sell_unit;
        total_cost += actual_sell_unit * stock_data[current_stockid]["buy_2_price"];
        sell_info->push_back(make_pair(stock_data[current_stockid]["buy_2_price"], (int)actual_sell_unit * 100));
    }
    
    if (already_sell_unit_amount <= want_unit_amount){
        has_unit_num = stock_data[current_stockid]["buy_3_amount"] / 100;
        actual_sell_unit = min(has_unit_num, want_unit_amount-already_sell_unit_amount);
        already_sell_unit_amount += actual_sell_unit;
        total_cost += actual_sell_unit * stock_data[current_stockid]["buy_3_price"];
        sell_info->push_back(make_pair(stock_data[current_stockid]["buy_3_price"], (int)actual_sell_unit * 100));
    }
    
    mean_sell_price[get_stock_index(current_stockid)] = -1;

    if (already_sell_unit_amount >= want_unit_amount && already_sell_unit_amount != 0)
    {
        mean_sell_price[get_stock_index(current_stockid)] = total_cost / already_sell_unit_amount;
    }
}


//register a listener
void StrategyPair::update(const string& stock_data_str, Trader* trader)
{
    dlog->info(stock_data_str);

    vector<string> tmp_v;
    util.split(stock_data_str, ",", tmp_v);
    string stockid = tmp_v[0];

    if (check_and_parse(tmp_v, stock_data))
    {
        get_buy_info(stockid);
        get_sell_info(stockid);
        run();

    }else{
        cerr << ">>> parse data error." << endl;
    }
}


void StrategyPair::run()
{
    last_stock_delta = current_stock_delta;

    time_t now_time;
    time(&now_time);
    minutes_to_closemarket = util.get_minutes_to_closemarket(now_time);

    if (-1 == minutes_to_closemarket)
        return;
    else if (1 == minutes_to_closemarket)
        close_today();
    else if (120.5 == minutes_to_closemarket)
        util.wait_for_half_open(now_time);

    if (-1 == mean_buy_price[0] || -1 == mean_buy_price[1] \
        -1 == mean_sell_price[0] || -1 == mean_sell_price[1])
        return;

    float current_relative_price1 = (mean_buy_price[0] - stock_data[stock_id1]["yesterday_close_price"]) / stock_data[stock_id1]["yesterday_close_price"];
    float current_relative_price2 = (mean_sell_price[1] - stock_data[stock_id2]["yesterday_close_price"]) / stock_data[stock_id2]["yesterday_close_price"];
    if (0.11 < fabs(current_relative_price1) || 0.11 < fabs(current_relative_price2))
    {
        cerr << ">>> ERROR, data overflow." << endl;
        return;
    }
    (*current_delta_relative_prices)[0] = current_relative_price2 - current_relative_price1;

    current_relative_price1 = (mean_sell_price[0] - stock_data[stock_id1]["yesterday_close_price"]) / stock_data[stock_id1]["yesterday_close_price"];
    current_relative_price2 = (mean_buy_price[1] - stock_data[stock_id2]["yesterday_close_price"]) / stock_data[stock_id2]["yesterday_close_price"];
    if (0.11 < fabs(current_relative_price1) || 0.11 < fabs(current_relative_price2))
    {
        cerr << ">>> ERROR, data overflow." << endl;
        return;
    }
    (*current_delta_relative_prices)[1] = current_relative_price1 - current_relative_price2;

    //TODO: deltainfo log
    
    (*max_delta_of_today)[0] = max(max((*max_delta_of_today)[0], \
                                   (*current_delta_relative_prices)[0]), \
                                   (*current_delta_relative_prices)[1]);
    (*min_delta_of_today)[0] = min(min((*max_delta_of_today)[0], \
                                   (*current_delta_relative_prices)[0]), \
                                   (*current_delta_relative_prices)[1]);
    (*current_stock_delta)[0] = (stock_data[stock_id1]["current_price"] - stock_data[stock_id1]["yesterday_close_price"]) / stock_data[stock_id1]["yesterday_close_price"];
    (*max_delta_of_today)[0] = max((*max_delta_of_today)[0], \
                                   (*current_stock_delta)[0]);
    (*min_delta_of_today)[0] = min((*max_delta_of_today)[0], \
                                   (*current_stock_delta)[0]);
    (*min_span_delta_of_today)[0] = min((*min_span_delta_of_today)[0], \
                                        (*current_stock_delta)[0] - (*current_stock_delta)[1]);
    (*current_stock_delta)[1] = (stock_data[stock_id2]["current_price"] - stock_data[stock_id2]["yesterday_close_price"]) / stock_data[stock_id2]["yesterday_close_price"];
    (*max_delta_of_today)[1] = max((*max_delta_of_today)[1], \
                                   (*current_stock_delta)[1]);
    (*min_delta_of_today)[1] = min((*max_delta_of_today)[1], \
                                   (*current_stock_delta)[1]);
    (*min_span_delta_of_today)[1] = min((*min_span_delta_of_today)[1], \
                                        (*current_stock_delta)[1] - (*current_stock_delta)[0]);

    if (want_sell_index != -1 && if_leave_time_right())
    {
        //clear position
        clear_yesterday_position();
        //TODO: log info
    }

    //TODO:check_stop_buy()
    check_stop_buy();

    if (0 != today_bought_stock.size() && false == stop_buy_flag)
    {
        for (int stock_index = 0; stock_index <= 1; ++stock_index)
        {
            if (true == if_enter_market(stock_index))
            {
                //TODO: money reserve
                //buy log 
                trigger_buy(stock_index);
                today_bought_stock = get_stock_id(stock_index);
                break;
            }
        }
    }

}

bool StrategyPair::if_leave_time_right()
{
    return false;
}


//finish today's work
void StrategyPair::close_today()
{
    //log todays trades
    //TODO: update volatility

}

void StrategyPair::check_stop_buy()
{
    //set stop_buy_flag
}

void StrategyPair::clear_yesterday_position()
{
    int total_sell_num = 0;
    float total_sell_price = 0.0;
    vector<pair<float, int> >* sell_info = NULL;

    if (want_sell_stockid == stock_id1) 
    {
        sell_info = sell_info1;
    }
    else if (want_sell_stockid == stock_id2) 
    {
        sell_info = sell_info2;
    }
    else{
        cerr << ">>> want_sell_stockid ERROR!" << endl;
        return;
    }

    for (vector<pair<float, int> >::iterator iter = sell_info->begin();
            iter != sell_info->end(); ++iter)
    {
        total_sell_price += iter->first;
        total_sell_num += iter->second;
    }

    if (0 == total_sell_num)
    {
        cout << "||| total_sell_num is 0." << endl;
        return;
    }

    string price = util.dtostring(total_sell_price / total_sell_num - 0.05);
    df->sell(want_sell_stockid, price, total_sell_num);
    float profit = total_sell_num * ((total_sell_price / total_sell_num - 0.05)- want_sell_stock_enter_price) - 32; // minus the fee
    want_sell_stockid = "";
    //TODO: log
}

void StrategyPair::trigger_buy(int stock_index)
{
    int total_buy_num = 0;
    float total_buy_price = 0.0;
    vector<pair<float, int> >* buy_info = NULL;
    string stock_id = get_stock_id(stock_index);

    if (stock_id == stock_id1) 
    {
        buy_info = buy_info1;
    }
    else if (stock_id == stock_id2) 
    {
        buy_info = buy_info2;
    }
    else{
        cerr << ">>> stock_id ERROR!" << endl;
        return;
    }

    for (vector<pair<float, int> >::iterator iter = buy_info->begin();
            iter != buy_info->end(); ++iter)
    {
        total_buy_price += iter->first;
        total_buy_num += iter->second;
    }

    if (0 == total_buy_num)
    {
        cout << "||| total_buy_num is 0." << endl;
        return;
    }

    string price = util.dtostring(total_buy_price / total_buy_num);
    df->buy(stock_id, price, total_buy_num);
    today_buy_price = total_buy_price / total_buy_num;
    today_buy_amout = total_buy_num;
}

bool StrategyPair::if_enter_market(int stock_index)
{
    int pair_stock_index = -1;
    if (0 == stock_index) pair_stock_index = 1;
    if (1 == stock_index) pair_stock_index = 0;
    
    if ((*current_stock_delta)[pair_stock_index] >= 0.025
            && (*max_delta_of_today)[pair_stock_index] - (*current_stock_delta)[pair_stock_index] < 0.01
            && (((*current_stock_delta)[stock_index] - (*min_delta_of_today)[stock_index] > 0.01) || (*current_stock_delta)[stock_index] >= 0)
            && (*current_stock_delta)[stock_index] < 0.025
            && (*current_delta_relative_prices)[stock_index] >= get_delta_threshold_of_entering_market())
    {
        return true;
    }
    return false;
}

//pair relative delta threshold variate by time
float StrategyPair::get_delta_threshold_of_entering_market()
{
    if (minutes_to_closemarket > 235 && minutes_to_closemarket <= 240)
        return base_enter_threshold - 0.006;
    else if (minutes_to_closemarket > 210 && minutes_to_closemarket <= 235)
        return base_enter_threshold - 0.004;
    else if (minutes_to_closemarket > 180 && minutes_to_closemarket <= 210)
        return base_enter_threshold - 0.002;
    else if (minutes_to_closemarket > 120 && minutes_to_closemarket <= 180)
        return base_enter_threshold;
    else if (minutes_to_closemarket > 0 && minutes_to_closemarket <= 120)
        return 100;

    return 100;
}
