#ifndef _TRADER_H__
#define _TRADER_H__

#include <string>
#include <vector>
#include <iostream>
#include <map>
#include "ThostFtdcTraderApiSSE.h"
#include "ThostFtdcUserApiDataTypeSSE.h"

using namespace std;

class Trader : public CZQThostFtdcTraderSpi
{
public:
	Trader(string front_address, string brokerID, string userID, string passwd){
		this->front_address = front_address;
		this->brokerID = brokerID;
		this->userID = userID;
		this->passwd = passwd;
		m_pTradeApi = CZQThostFtdcTraderApi::CreateFtdcTraderApi("/tmp/CTP_LTS_trade/");
		this->init();
		this->ExchangeIDDict["sh"] = "SSE";
		this->ExchangeIDDict["sz"] = "SZE";
		this->ExchangeIDDict_Reverse["SSE"] = "sh";
		this->ExchangeIDDict_Reverse["SZE"] = "sz";
		m_pTradeApi->SubscribePrivateTopic(ZQTHOST_TERT_RESUME);
		m_pTradeApi->SubscribePublicTopic(ZQTHOST_TERT_RESUME);
	}
	
	~Trader(){
		m_pTradeApi->Release();
	}

	void buy(string stockid, string limit_price, int amount);
	void sell(string stockid, string limit_price, int amount);
	void update_position_info();
	map< string, int > get_position_info();
	void update_account_info();
	map< string, double > get_account_info();
	void update_trade_records();
	vector< string > get_trade_records();

	bool IsErrorRspInfo(CZQThostFtdcRspInfoField *pRspInfo);
	string get_error_msg(){ return error_msg; }

private:
	static int m_sRequestID;
	static int m_sOrderRef;
	CZQThostFtdcTraderApi *m_pTradeApi;
	string brokerID;
	string userID;
	string passwd;
	string front_address;
	map< string, string > ExchangeIDDict;
	map< string, string > ExchangeIDDict_Reverse;
	map< string, double > account_info;
	map< string, int > position_info;
	vector< string > trade_records;
	string error_msg;

	void init();
	void OnFrontConnected();
	void trade(string stockID, string exchangeID, string limit_price, int amount, TZQThostFtdcDirectionType direction);

	void OnRtnOrder(CZQThostFtdcOrderField *pOrder);
	void OnRspError(CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	void OnRtnTrade(CZQThostFtdcTradeField *pTrade);
	
	void OnRspUserLogin(CZQThostFtdcRspUserLoginField *pRspUserLogin, CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	void OnRspOrderInsert(CZQThostFtdcInputOrderField *pInputOrder,CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	void OnRspQryInvestorPosition(CZQThostFtdcInvestorPositionField *pInvestorPosition, CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	void OnRspQryTradingAccount(CZQThostFtdcTradingAccountField *pTradingAccount, CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	void OnRspQryTrade(CZQThostFtdcTradeField *pTrade, CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

};

#endif /* end of include guard: _TRADER_H__ */

