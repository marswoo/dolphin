#ifndef _DATAFEEDER_H__
#define _DATAFEEDER_H__

#include <string>
#include <map>
#include "ThostFtdcMdApiSSE.h"
#include "ThostFtdcUserApiStructSSE.h"

using namespace std;

class DataFeeder : public CZQThostFtdcMdSpi
{
public:
    DataFeeder(string front_address, string brokerID, string userID, string passwd){
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

    ~DataFeeder(){
        this->m_pMdApi->Release();
    }

	void subscrib_market_data(string InstrumentID);
	string get_market_data(string InstrumentID);

private:
    CZQThostFtdcMdApi *m_pMdApi;
    string brokerID;
    string userID;
    string passwd;
    string front_address;
    map< string, string > ExchangeIDDict;
    map< string, string > ExchangeIDDict_Reverse;
    map< string, string > stock_datas;

	void init();
	void OnFrontConnected();
	void OnRspUserLogin(CZQThostFtdcRspUserLoginField *pRspUserLogin, CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	void OnRtnDepthMarketData(CZQThostFtdcDepthMarketDataField *pDepthMarketData);
};

#endif /* end of include guard: _DATAFEEDER_H__ */

