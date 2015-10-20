#include <sstream>
#include <iostream>
#include <cstring>
#include "datafeeder.h"

//inherited behaviors
void DataFeeder::init()
{
    m_pMdApi->RegisterSpi(this);
    m_pMdApi->RegisterFront(const_cast<char*>(this->front_address.c_str()));
    m_pMdApi->Init();
}

//inherited behaviors
void DataFeeder::OnFrontConnected()
{
	CZQThostFtdcReqUserLoginField reqUserLogin;
	memset(&reqUserLogin, 0, sizeof(reqUserLogin));
    strcpy(reqUserLogin.BrokerID, this->brokerID.c_str());
    strcpy(reqUserLogin.UserID, this->userID.c_str());
    strcpy(reqUserLogin.Password, this->passwd.c_str());
    m_pMdApi->ReqUserLogin(&reqUserLogin, 0);
}

//inherited behaviors
void DataFeeder::OnRspUserLogin(CZQThostFtdcRspUserLoginField *pRspUserLogin, CZQThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
    if (pRspInfo->ErrorID == 0)
    {
        cout << "--- Login Success!" << endl;
        cout << "--- OnRspUserLogin:\t" << "ReturnCode=[" << pRspInfo->ErrorID << "], Msg=[" << pRspInfo->ErrorMsg << "]" << endl;
    }
    else
    {
        cerr << "Login Error!" << endl;
        cerr << "OnRspUserLogin:\t" << "ReturnCode=[" << pRspInfo->ErrorID << "], Msg=[" << pRspInfo->ErrorMsg << "]" << endl;
    }
}

//inherited behaviors
//callback function, trigger to notify listener
void DataFeeder::OnRtnDepthMarketData(CZQThostFtdcDepthMarketDataField *pDepthMarketData)
{
	ostringstream oss;
	CZQThostFtdcDepthMarketDataField *p = pDepthMarketData;
	string stockid = this->ExchangeIDDict_Reverse[p->ExchangeID] + p->InstrumentID;

	oss << stockid << ',' << p->TradingDay << ',' << p->UpdateTime << ','
		<< p->LastPrice << ',' << p->PreClosePrice << ',' << p->OpenPrice << ',' 
        << p->ClosePrice << ',' << p->HighestPrice << ',' << p->LowestPrice << ',' 
		<< p->Volume << ',' << p->Turnover << ',' << p->BidPrice1 << ',' 
        << p->BidVolume1 << ',' << p->BidPrice2 << ',' << p->BidVolume2 << ',' 
        << p->BidPrice3 << ',' << p->BidVolume3 << ',' << p->AskPrice1 << ',' 
        << p->AskVolume1 << ',' << p->AskPrice2 << ',' << p->AskVolume2 << ',' 
        << p->AskPrice3 << ',' << p->AskVolume3 << ',';
	
    Strategy* stra = this->strategies[stockid];
    this->notify(stra, oss.str());
}

//register a listener
void DataFeeder::register_stock_data(Strategy* stra)
{
    string stockid = stra->get_stock_id();
	std::string InstrumentID = stockid.substr(2);
	std::string ExchangeID = this->ExchangeIDDict[ stockid.substr(0,2) ];
	char* id = const_cast<char*>(InstrumentID.c_str());
	int result = m_pMdApi->SubscribeMarketData( &id, 1, const_cast<char*>(ExchangeID.c_str()) );
	if( result != 0)
    {
		cerr << ">>> Failed to subscribe " << ExchangeID << ":" << InstrumentID<< endl;
    }
	else
    {
        if (0 != this->strategies.count(stockid))
        {
            delete this->strategies[stockid];
        } 
        else
        {
            this->strategies[stockid] = stra;
            cerr << ">>> Success to subscribe " << ExchangeID << ":" << InstrumentID<< endl;
        }
    }
}

//unregister a listener
void DataFeeder::un_register_stock_data(Strategy* stra)
{
    string stockid = stra->get_stock_id();
	std::string InstrumentID = stockid.substr(2);
	std::string ExchangeID = this->ExchangeIDDict[ stockid.substr(0,2) ];
	char* id = const_cast<char*>(InstrumentID.c_str());
	int result = m_pMdApi->UnSubscribeMarketData( &id, 1, const_cast<char*>(ExchangeID.c_str()) );
	if( result != 0)
    {
        if (0 != this->strategies.count(stockid))
        {
            delete this->strategies[stockid];
        } 
		cerr << ">>> Failed to un_subscribe " << ExchangeID << ":" << InstrumentID<< endl;
    }
	else
    {
		cout << "--- Success to un_subscribe " << ExchangeID << ":" << InstrumentID<< endl;
    }
}

//notiry listener
void DataFeeder::notify(Strategy* stra, const string& stock_data)
{
    stra->update(stock_data);
}

int main()
{
    Strategy* stra1 = new Strategy("sh600216");
    Strategy* stra2 = new Strategy("sz002001");
    DataFeeder* df = new DataFeeder("tcp://180.166.11.40:41213", "2011", "20000479", "154097");
    sleep(1);
    df->register_stock_data(stra1);
    df->register_stock_data(stra2); 
    return 0;
}
