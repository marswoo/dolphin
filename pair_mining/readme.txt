The propose of this experiment is to find pairs for Dolphin system.
对每只股票每日的涨跌幅形成的序列当做表征该股票的向量；
考察任意两只股票向量之间的相似度，作为股票价格走势的相似度值；
计算相似度拟采用三种距离：余弦距离、皮尔逊距离、欧氏距离；
通过对相似度高的pair进行人工review、考察离线Dolphin效果来得到新pair；
也可参考反应股票波动幅度的振幅。

* prepare.sh(py) : 预处理天级数据；
* calculate_distance.py : 计算股票之间相似度，可以选取三种距离：余弦距离、皮尔逊距离、欧氏距离，还可以选取开始时间；
* volatility.py : 计算每只股票波动率；
* pair_volatility.py : 计算股票pair波动率；
* normalize.py : 为每种距离或波动率做归一化处理；
* final_score.py : 通过对多个距离和波动率进行加权，得到最终得分；
* find_candidate_pairs.py : 分行业找最相近的top pairs；

* addTimeToData.py : 为分钟级数据增加分钟时间，用于跑Dolphin测试；
* google_distance.py : 通过google查询结果计算pair相似度；

**需要定时更新stocklist数据**
