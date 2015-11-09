#include <sstream>
#include <iostream>
#include <cstring>

#include "datafeeder.h"
#include "strategy_pair.h"

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
        cerr << ">>> Datafeeder Login Error!" << endl;
        cerr << ">>> OnRspUserLogin:\t" << "ReturnCode=[" << pRspInfo->ErrorID << "], Msg=[" << pRspInfo->ErrorMsg << "]" << endl;
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
    
    this->notify(stockid, oss.str());
}

//register a listener
void DataFeeder::register_stock_data(const string& stockid, Observer* stra)
{
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
        this->strategies[stockid] = stra;
        cout << "--- Success to subscribe " << ExchangeID << ":" << InstrumentID<< endl;
    }
}

//unregister a listener
void DataFeeder::un_register_stock_data(const string& stockid, Observer* stra)
{
    std::string InstrumentID = stockid.substr(2);
    std::string ExchangeID = this->ExchangeIDDict[ stockid.substr(0,2) ];
    char* id = const_cast<char*>(InstrumentID.c_str());
    int result = m_pMdApi->UnSubscribeMarketData( &id, 1, const_cast<char*>(ExchangeID.c_str()) );
    if( result != 0)
    {
        cerr << ">>> Failed to un_subscribe " << ExchangeID << ":" << InstrumentID<< endl;
    }
    else
    {
        if (strategies.count(stockid) != 0)
        {
            delete strategies[stockid];
        }
        cout << "--- Success to un_subscribe " << ExchangeID << ":" << InstrumentID<< endl;
    }
}

//notiry listener
void DataFeeder::notify(const string& stockid, const string& stock_data)
{
    strategies[stockid]->update(stock_data, trader);
}

void DataFeeder::buy(string stockid, string limit_price, int amount)
{
    this->trader->buy(stockid, limit_price, amount);
}

void DataFeeder::sell(string stockid, string limit_price, int amount)
{
    this->trader->sell(stockid, limit_price, amount);
}


void DataFeeder::display_status()
{
    cout << "Observers:" << endl;
    for (map<string, Observer* >::iterator iter = strategies.begin();
            iter != strategies.end();
            ++iter)
    {
        cout << iter -> first << endl;
        cout << iter -> second << endl;
    }
}

int main()
{
    DataFeeder* df = new DataFeeder("tcp://180.166.11.40:41213", "2011", "20000479", "154097");
    StrategyPair* stra1 = new StrategyPair("sh600031_sz000157", df);
    StrategyPair* stra2 = new StrategyPair("sz002001_sh600216", df);
    StrategyPair* stra3 = new StrategyPair("sh601601_sh601628", df);

    sleep(1);
    df->register_stock_data(stra1->get_stock_id(0), stra1);
    df->register_stock_data(stra1->get_stock_id(1), stra1);
    df->register_stock_data(stra2->get_stock_id(0), stra2);
    df->register_stock_data(stra2->get_stock_id(1), stra2);
    df->register_stock_data(stra3->get_stock_id(0), stra3);
    df->register_stock_data(stra3->get_stock_id(1), stra3);
    //df->display_status();
    //df->buy("sh600216", "100", 200);

    while(true){
        sleep(1);
    }
    return 0;
}
