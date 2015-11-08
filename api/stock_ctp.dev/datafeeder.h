#ifndef _DATAFEEDER_H__
#define _DATAFEEDER_H__

#include <string>
#include <map>
#include <unistd.h>
#include "ThostFtdcMdApiSSE.h"
#include "ThostFtdcUserApiStructSSE.h"
#include "trader.h"
#include "util.h"
#include "observer.h"

using namespace std;

class DataFeeder : public CZQThostFtdcMdSpi
{
public:
    DataFeeder(const string& front_address, 
               const string& brokerID, 
               const string& userID, 
               const string& passwd)
    {
        this->trader = new Trader("tcp://180.166.11.40:41205", "2011", "20000479", "154097");
        sleep(1);
        this->front_address = front_address;
        this->brokerID = brokerID;
        this->userID = userID;
        this->passwd = passwd;
        this->m_pMdApi = CZQThostFtdcMdApi::CreateFtdcMdApi("/tmp/CTP_LTS_data/");
        this->init();
        this->ExchangeIDDict["sh"] = "SSE";
        this->ExchangeIDDict["sz"] = "SZE";
        this->ExchangeIDDict_Reverse["SSE"] = "sh";
        this->ExchangeIDDict_Reverse["SZE"] = "sz";
    }

    ~DataFeeder()
    {
        this->m_pMdApi->Release();
        delete trader;
    }

	void register_stock_data(const string& stockid, Observer* stra);
	void un_register_stock_data(const string& stockid, Observer* stra);
    void notify(const string& stockid, const string& stock_data);
    void buy(string stockid, string limit_price, int amount);
    void sell(string stockid, string limit_price, int amount);
    void display_status();

    Trader *trader;

private:
    CZQThostFtdcMdApi *m_pMdApi;
    Util util;

    string brokerID;
    string userID;
    string passwd;
    string front_address;

    map<string, string> ExchangeIDDict;
    map<string, string> ExchangeIDDict_Reverse;
    map<string, Observer* > strategies;

	void init();
	void OnFrontConnected();
	void OnRspUserLogin(CZQThostFtdcRspUserLoginField *pRspUserLogin, CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	void OnRtnDepthMarketData(CZQThostFtdcDepthMarketDataField *pDepthMarketData);
};

#endif /* end of include guard: _DATAFEEDER_H__ */

