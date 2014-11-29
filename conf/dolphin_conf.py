#coding: utf8

BUY_STRATEGY_OPTIONS = {'Buy_low':0, 'Buy_high':1}

COMMON_CONF = {
    "each_deal_expense" : 20000.0,
    "yesterday_position_file_path" : "/tmp/OnesideDolphin/YesterdayPosition/",
    "base_enter_threshold" : 0.013,
    "buy_strategy" : BUY_STRATEGY_OPTIONS["Buy_low"],
    "retrive_data_interval" : 4,
    "stock_relative_val_thr" : 0.11,
    "self.base_enter_threshold" : 0.013,
}
