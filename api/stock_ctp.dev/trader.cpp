#include <cstring>
#include <cstdio>
#include <sstream>
#include "trader.h"

int Trader::m_sOrderRef = 0;
int Trader::m_sRequestID = 0;

void Trader::init()
{
	m_pTradeApi->RegisterSpi(this);
	m_pTradeApi->RegisterFront(const_cast<char*>(this->front_address.c_str()));
	// client connect server
	m_pTradeApi->Init();
}

void Trader::OnFrontConnected()
{
	CZQThostFtdcReqUserLoginField reqUserLogin;
	memset(&reqUserLogin, 0, sizeof(reqUserLogin));
	strcpy(reqUserLogin.BrokerID, this->brokerID.c_str());
	strcpy(reqUserLogin.UserID, this->userID.c_str());
	strcpy(reqUserLogin.Password, this->passwd.c_str());
	int rt = m_pTradeApi->ReqUserLogin(&reqUserLogin, ++m_sRequestID);
    if (0 != rt)
    {
		cerr << ">>> ErrorInfo: ReqUserLogin Error." << endl;
    }
}

void Trader::OnRspUserLogin(CZQThostFtdcRspUserLoginField *pRspUserLogin, CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	bool rt = IsErrorRspInfo(pRspInfo);
    if (true == rt){
        cerr << ">>> IsErrorRspInfo" << endl;
    }
}

bool Trader::IsErrorRspInfo(CZQThostFtdcRspInfoField *pRspInfo)
{
	bool bResult = ((pRspInfo) && (pRspInfo->ErrorID != 0));
	if (bResult)
    {
		cerr << ">>> ErrorID=" 
             << pRspInfo->ErrorID 
             << ", ErrorMsg=" 
             << pRspInfo->ErrorMsg 
             << endl;
		this->error_msg = pRspInfo->ErrorMsg;
	}
	return bResult;
}

void Trader::buy(string stockid, string limit_price, int amount)
{
	this->trade(stockid.substr(2), this->ExchangeIDDict[stockid.substr(0,2)], limit_price, amount, THOST_FTDC_D_Buy);
}

void Trader::sell(string stockid, string limit_price, int amount)
{
	this->trade(stockid.substr(2), this->ExchangeIDDict[stockid.substr(0,2)], limit_price, amount, THOST_FTDC_D_Sell);
}

void Trader::trade(string stockID, string exchangeID, string limit_price, int amount, TZQThostFtdcDirectionType direction)
{
	CZQThostFtdcInputOrderField req;
	memset(&req, 0, sizeof(req));
	
	strcpy(req.BrokerID, this->brokerID.c_str());
	strcpy(req.InvestorID, this->userID.c_str());
	req.OrderPriceType = THOST_FTDC_OPT_LimitPrice;

	strcpy(req.InstrumentID, stockID.c_str());
	strcpy(req.ExchangeID, exchangeID.c_str());
	strcpy(req.LimitPrice, limit_price.c_str());
	req.VolumeTotalOriginal = amount;
	req.Direction = direction;
	
	char buffer[10];
	sprintf(buffer, "%d", m_sOrderRef++);
	strcpy(req.OrderRef, buffer);
	
	req.TimeCondition = THOST_FTDC_TC_GFD;
	req.VolumeCondition = THOST_FTDC_VC_AV;
	req.ContingentCondition = THOST_FTDC_CC_Immediately;
	req.ForceCloseReason = THOST_FTDC_FCC_NotForceClose;
	
	req.UserForceClose = 0;
	req.RequestID = ++m_sRequestID;
	
	m_pTradeApi->ReqOrderInsert(&req, m_sRequestID);
}

void Trader::OnRspOrderInsert(CZQThostFtdcInputOrderField *pInputOrder,CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast){
	cout << "--- OnRspOrderInsert" << endl;
	bool rt = IsErrorRspInfo(pRspInfo);
    if (true == rt){
        cerr << ">>> IsErrorRspInfo Error!" << endl;
    }
}

void Trader::OnRtnTrade(CZQThostFtdcTradeField *pTrade)
{
	cout << "--- Trade notification: \n" 
         << pTrade->InstrumentID << '\t' 
         << pTrade->Direction << '\t' 
         << pTrade->Price << '\t' 
         << pTrade->Volume << '\t' 
         << pTrade->TradeDate << '\t' 
         << pTrade->TradeTime << endl;
}

void Trader::OnRtnOrder(CZQThostFtdcOrderField *pOrder)
{
	cout << "--- Order Return notification: \n" 
         << pOrder->InstrumentID << '\t' 
         << pOrder->LimitPrice << '\t' 
         << pOrder->VolumeTraded << endl;
}

// 针对用户请求的出错通知
void Trader::OnRspError(CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	bool rt = IsErrorRspInfo(pRspInfo);
    if (true == rt){
        cerr << ">>> OnRspError Error!" << endl;
    }
}

void Trader::update_position_info()
{
	position_info.clear();
	CZQThostFtdcQryInvestorPositionField query;
	memset(&query, 0, sizeof(query));
	strcpy(query.BrokerID, this->brokerID.c_str());
	strcpy(query.InvestorID, this->userID.c_str());
	m_pTradeApi->ReqQryInvestorPosition(&query, ++m_sRequestID);
}

map< string, int > Trader::get_position_info()
{
	return this->position_info;
}

void Trader::OnRspQryInvestorPosition(CZQThostFtdcInvestorPositionField *pInvestorPosition, CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	if( pInvestorPosition )
	{
		string stockid = ExchangeIDDict_Reverse[pInvestorPosition->ExchangeID] + pInvestorPosition->InstrumentID;
		this->position_info[ stockid ] = pInvestorPosition->YdPosition;
	}
}

void Trader::update_account_info()
{
	CZQThostFtdcQryTradingAccountField query;
	memset(&query, 0, sizeof(query));
	strcpy(query.BrokerID, this->brokerID.c_str());
	strcpy(query.InvestorID, this->userID.c_str());
	bool rt = m_pTradeApi->ReqQryTradingAccount(&query, ++m_sRequestID);
    if (0 != rt){
		cerr << ">>> ErrorInfo: ReqQryTradingAccount Error." << endl;
    }
}

map< string, double > Trader::get_account_info()
{
	return this->account_info;
}

void Trader::OnRspQryTradingAccount(CZQThostFtdcTradingAccountField *pTradingAccount, CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	if( pTradingAccount )
	{
		this->account_info["Available"] = pTradingAccount->Available;
		this->account_info["Commission"] = pTradingAccount->Commission;
		this->account_info["Balance"] = pTradingAccount->Balance;
		this->account_info["WithdrawQuota"] = pTradingAccount->WithdrawQuota;
		this->account_info["Reserve"] = pTradingAccount->Reserve;
		this->account_info["Credit"] = pTradingAccount->Credit;
	}else{
		cerr << ">>> ErrorInfo: pTradingAccount is NULL." << endl;
    }
}

void Trader::update_trade_records()
{
	trade_records.clear();
	CZQThostFtdcQryTradeField query;
	memset(&query, 0, sizeof(query));
	strcpy(query.BrokerID, this->brokerID.c_str());
	strcpy(query.InvestorID, this->userID.c_str());
	m_pTradeApi->ReqQryTrade(&query, ++m_sRequestID);
}

vector< string > Trader::get_trade_records()
{
	return this->trade_records;
}

void Trader::OnRspQryTrade(CZQThostFtdcTradeField *pTrade, CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	if( pTrade )
	{
		ostringstream oss;
		oss << pTrade->TradeDate << '\t' 
            << pTrade->TradeTime << '\t' 
            << pTrade->Direction << '\t' 
            << ExchangeIDDict_Reverse[pTrade->ExchangeID] 
            << pTrade->InstrumentID << '\t' 
            << pTrade->Price << '\t' 
            << pTrade->Volume;
		this->trade_records.push_back( oss.str() );
	}
}

int main(){

    Trader* df = new Trader("tcp://180.166.11.40:41213", "2011", "20000479", "154097");
    return 0;
}
