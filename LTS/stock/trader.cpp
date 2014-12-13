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
	// 使客户端开始与后台服务建立连接
	m_pTradeApi->Init();
}

void Trader::OnFrontConnected()
{
	CSecurityFtdcReqUserLoginField reqUserLogin;
	memset(&reqUserLogin, 0, sizeof(reqUserLogin));
	strcpy(reqUserLogin.BrokerID, this->brokerID.c_str());
	strcpy(reqUserLogin.UserID, this->userID.c_str());
	strcpy(reqUserLogin.Password, this->passwd.c_str());
	int rt = m_pTradeApi->ReqUserLogin(&reqUserLogin, ++m_sRequestID);
    if (0 != rt){
		cerr << "------>>>>>> ErrorInfo: ReqUserLogin error." << endl;
    }
}

void Trader::OnRspUserLogin(CSecurityFtdcRspUserLoginField *pRspUserLogin, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	cerr << "--->>> OnRspUserLogin" << endl;
	IsErrorRspInfo(pRspInfo);
}

bool Trader::IsErrorRspInfo(CSecurityFtdcRspInfoField *pRspInfo)
{
	bool bResult = ((pRspInfo) && (pRspInfo->ErrorID != 0));
	if (bResult){
		cerr << "------>>>>>> ErrorID=" << pRspInfo->ErrorID << ", ErrorMsg=" << pRspInfo->ErrorMsg << endl;
		this->error_msg = pRspInfo->ErrorMsg;
	}
	return bResult;
}

void Trader::buy(string stockid, string limit_price, int amount)
{
	this->trade(stockid.substr(2), this->ExchangeIDDict[stockid.substr(0,2)], limit_price, amount, SECURITY_FTDC_D_Buy);
}

void Trader::sell(string stockid, string limit_price, int amount)
{
	this->trade(stockid.substr(2), this->ExchangeIDDict[stockid.substr(0,2)], limit_price, amount, SECURITY_FTDC_D_Sell);
}

void Trader::trade(string stockID, string exchangeID, string limit_price, int amount, TSecurityFtdcDirectionType direction)
{
	CSecurityFtdcInputOrderField req;
	memset(&req, 0, sizeof(req));
	
	strcpy(req.BrokerID, this->brokerID.c_str());
	strcpy(req.InvestorID, this->userID.c_str());
	req.OrderPriceType = SECURITY_FTDC_OPT_LimitPrice;

	strcpy(req.InstrumentID, stockID.c_str());
	strcpy(req.ExchangeID, exchangeID.c_str());
	strcpy(req.LimitPrice, limit_price.c_str());
	req.VolumeTotalOriginal = amount;
	req.Direction = direction;
	
	char buffer[10];
	sprintf(buffer, "%d", m_sOrderRef++);
	strcpy(req.OrderRef, buffer);
	
	req.TimeCondition = SECURITY_FTDC_TC_GFD;
	req.VolumeCondition = SECURITY_FTDC_VC_AV;
	req.ContingentCondition = SECURITY_FTDC_CC_Immediately;
	req.ForceCloseReason = SECURITY_FTDC_FCC_NotForceClose;
	
//	req.CombOffsetFlag[0]=SECURITY_FTDC_OF_Open;
//	req.CombHedgeFlag[0]=SECURITY_FTDC_HF_Speculation;
//	req.MinVolume=1;
//	req.IsAutoSuspend = 0;
	req.UserForceClose = 0;
	req.RequestID = ++m_sRequestID;
	
	m_pTradeApi->ReqOrderInsert(&req, m_sRequestID);
}

void Trader::OnRspOrderInsert(CSecurityFtdcInputOrderField *pInputOrder,CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast){
	// 输出报单录入结果
	cout << "--->>> OnRspOrderInsert" << endl;
	IsErrorRspInfo(pRspInfo);
}

void Trader::OnRtnTrade(CSecurityFtdcTradeField *pTrade)
{
	cout << "--->>> Trade notification: \n" << pTrade->InstrumentID << '\t' << pTrade->Direction << '\t' << pTrade->Price << '\t' << pTrade->Volume << '\t' << pTrade->TradeDate << ' ' << pTrade->TradeTime << endl;
}

void Trader::OnRtnOrder(CSecurityFtdcOrderField *pOrder)
{
	cout << "--->>> Order Return notification: \n" << pOrder->InstrumentID << '\t' << pOrder->LimitPrice << '\t' << pOrder->VolumeTraded << endl;
}

// 针对用户请求的出错通知
void Trader::OnRspError(CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	cerr << "--->>> OnRspError" << endl;
	IsErrorRspInfo(pRspInfo);
}

void Trader::update_position_info()
{
	position_info.clear();

	CSecurityFtdcQryInvestorPositionField query;
	memset(&query, 0, sizeof(query));
	strcpy(query.BrokerID, this->brokerID.c_str());
	strcpy(query.InvestorID, this->userID.c_str());
	m_pTradeApi->ReqQryInvestorPosition(&query, ++m_sRequestID);
}

map< string, int > Trader::get_position_info()
{
	return this->position_info;
}

void Trader::OnRspQryInvestorPosition(CSecurityFtdcInvestorPositionField *pInvestorPosition, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	if( pInvestorPosition )
	{
		string stockid = ExchangeIDDict_Reverse[pInvestorPosition->ExchangeID] + pInvestorPosition->InstrumentID;
		this->position_info[ stockid ] = pInvestorPosition->YdPosition;
	}
}

void Trader::update_account_info()
{
	CSecurityFtdcQryTradingAccountField query;
	memset(&query, 0, sizeof(query));
	strcpy(query.BrokerID, this->brokerID.c_str());
	strcpy(query.InvestorID, this->userID.c_str());
	bool rt = m_pTradeApi->ReqQryTradingAccount(&query, ++m_sRequestID);
    if (0 != rt){
		cerr << "------>>>>>> ErrorInfo: ReqQryTradingAccount error." << endl;
    }
}

map< string, double > Trader::get_account_info()
{
	return this->account_info;
}

void Trader::OnRspQryTradingAccount(CSecurityFtdcTradingAccountField *pTradingAccount, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
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
		cerr << "------>>>>>> ErrorInfo: pTradingAccount is NULL." << endl;
    }
}

void Trader::update_trade_records()
{
	trade_records.clear();

	CSecurityFtdcQryTradeField query;
	memset(&query, 0, sizeof(query));

	strcpy(query.BrokerID, this->brokerID.c_str());
	strcpy(query.InvestorID, this->userID.c_str());
	m_pTradeApi->ReqQryTrade(&query, ++m_sRequestID);
}

vector< string > Trader::get_trade_records()
{
	return this->trade_records;
}

void Trader::OnRspQryTrade(CSecurityFtdcTradeField *pTrade, CSecurityFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	if( pTrade )
	{
		ostringstream oss;
		oss << pTrade->TradeDate << ' ' << pTrade->TradeTime << ' ' << pTrade->Direction << ' ' << ExchangeIDDict_Reverse[pTrade->ExchangeID] << pTrade->InstrumentID << ' ' << pTrade->Price << ' ' << pTrade->Volume;
		this->trade_records.push_back( oss.str() );
	}
}

