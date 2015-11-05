#include <iostream>
#include "strategy_pair.h"

//check stock_data_str and parse to map
bool StrategyPair::check_and_parse(vector<string>& tmp_v, map<string, map<string, float> > &stock_data)
{
    if (0 == atof(tmp_v[4].c_str()))
    {
        return false;
    }

    stock_data[tmp_v[0]]["current_price"] = atof(tmp_v[4].c_str());
    stock_data[tmp_v[0]]["yesterday_close_price"] = atof(tmp_v[5].c_str());
    stock_data[tmp_v[0]]["today_open_price"] = atof(tmp_v[6].c_str());
    stock_data[tmp_v[0]]["today_highest_price"] = atof(tmp_v[7].c_str());
    stock_data[tmp_v[0]]["today_lowest_price"] = atof(tmp_v[8].c_str());
    stock_data[tmp_v[0]]["volume"] = atof(tmp_v[9].c_str());
    stock_data[tmp_v[0]]["turnover"] = atof(tmp_v[10].c_str());
    stock_data[tmp_v[0]]["buy_1_price"] = atof(tmp_v[11].c_str());
    stock_data[tmp_v[0]]["buy_1_amount"] = atof(tmp_v[12].c_str());
    stock_data[tmp_v[0]]["buy_2_price"] = atof(tmp_v[13].c_str());
    stock_data[tmp_v[0]]["buy_2_amount"] = atof(tmp_v[14].c_str());
    stock_data[tmp_v[0]]["buy_3_price"] = atof(tmp_v[15].c_str());
    stock_data[tmp_v[0]]["buy_3_amount"] = atof(tmp_v[16].c_str());
    stock_data[tmp_v[0]]["sell_1_price"] = atof(tmp_v[17].c_str());
    stock_data[tmp_v[0]]["sell_1_amount"] = atof(tmp_v[18].c_str());
    stock_data[tmp_v[0]]["sell_2_price"] = atof(tmp_v[19].c_str());
    stock_data[tmp_v[0]]["sell_2_amount"] = atof(tmp_v[20].c_str());
    stock_data[tmp_v[0]]["sell_3_price"] = atof(tmp_v[21].c_str());
    stock_data[tmp_v[0]]["sell_3_amount"] = atof(tmp_v[22].c_str());

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
    buy_info->push_back(make_pair(stock_data[current_stockid]["sell_1_amount"], (int)actual_buy_unit * 100));

    if (already_buy_unit_amount <= want_unit_amount){
        has_unit_num = stock_data[current_stockid]["sell_2_amount"] / 100;
        actual_buy_unit = min(has_unit_num, want_unit_amount-already_buy_unit_amount);
        already_buy_unit_amount += actual_buy_unit;
        total_cost += actual_buy_unit * stock_data[current_stockid]["sell_2_price"];
        buy_info->push_back(make_pair(stock_data[current_stockid]["sell_2_amount"], (int)actual_buy_unit * 100));
    }
    
    if (already_buy_unit_amount <= want_unit_amount){
        has_unit_num = stock_data[current_stockid]["sell_3_amount"] / 100;
        actual_buy_unit = min(has_unit_num, want_unit_amount-already_buy_unit_amount);
        already_buy_unit_amount += actual_buy_unit;
        total_cost += actual_buy_unit * stock_data[current_stockid]["sell_3_price"];
        buy_info->push_back(make_pair(stock_data[current_stockid]["sell_3_amount"], (int)actual_buy_unit * 100));
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
    sell_info->push_back(make_pair(stock_data[current_stockid]["buy_1_amount"], (int)actual_sell_unit * 100));

    if (already_sell_unit_amount <= want_unit_amount){
        has_unit_num = stock_data[current_stockid]["buy_2_amount"] / 100;
        actual_sell_unit = min(has_unit_num, want_unit_amount-already_sell_unit_amount);
        already_sell_unit_amount += actual_sell_unit;
        total_cost += actual_sell_unit * stock_data[current_stockid]["buy_2_price"];
        sell_info->push_back(make_pair(stock_data[current_stockid]["buy_2_amount"], (int)actual_sell_unit * 100));
    }
    
    if (already_sell_unit_amount <= want_unit_amount){
        has_unit_num = stock_data[current_stockid]["buy_3_amount"] / 100;
        actual_sell_unit = min(has_unit_num, want_unit_amount-already_sell_unit_amount);
        already_sell_unit_amount += actual_sell_unit;
        total_cost += actual_sell_unit * stock_data[current_stockid]["buy_3_price"];
        sell_info->push_back(make_pair(stock_data[current_stockid]["buy_3_amount"], (int)actual_sell_unit * 100));
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
    cout << "--- stockdata: " << stock_data_str << endl;

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


bool StrategyPair::if_enter_market()
{
    return false;
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
}


//finish today's work
void StrategyPair::close_today()
{

}
