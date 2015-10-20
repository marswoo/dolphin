#ifndef _DATAFEEDER_H__
#define _DATAFEEDER_H__

#include <string>
#include <map>
#include <unistd.h>
#include "ThostFtdcMdApiSSE.h"
#include "ThostFtdcUserApiStructSSE.h"
#include "strategy.h"
#include "trader.h"

using namespace std;

class DataFeeder : public CZQThostFtdcMdSpi
{
public:
    DataFeeder(const string& front_address, 
               const string& brokerID, 
               const string& userID, 
               const string& passwd)
    {
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
        this->trader = new Trader(front_address, brokerID, userID, passwd);
    }

    ~DataFeeder()
    {
        this->m_pMdApi->Release();
        for (map<string, Strategy* >::iterator iter = strategies.begin(); iter != strategies.end(); ++iter)
        {
            delete iter->second;
        }
        delete trader;
    }

	void register_stock_data(Strategy* stra);
	void un_register_stock_data(Strategy* stra);
    void notify(Strategy* stra, const string& stock_data);

private:
    CZQThostFtdcMdApi *m_pMdApi;
    Trader *trader;

    string brokerID;
    string userID;
    string passwd;
    string front_address;

    map<string, string> ExchangeIDDict;
    map<string, string> ExchangeIDDict_Reverse;
    map<string, Strategy* > strategies;

	void init();
	void OnFrontConnected();
	void OnRspUserLogin(CZQThostFtdcRspUserLoginField *pRspUserLogin, CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	void OnRtnDepthMarketData(CZQThostFtdcDepthMarketDataField *pDepthMarketData);
};

#endif /* end of include guard: _DATAFEEDER_H__ */

