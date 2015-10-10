#ifndef _STRATEGY_H__
#define _STRATEGY_H__

#include <string>
#include "ThostFtdcMdApiSSE.h"
#include "ThostFtdcUserApiStructSSE.h"
#include "observer.h"

using namespace std;

class Strategy : public Observer
{
public:
    Strategy(const string& stock_id)
    {
        this->stock_id = stock_id;
    }

    ~Strategy()
    {
    }

    virtual void update(const string& stock_data);

    string get_stock_id()
    {
        return this->stock_id;
    }
private:
    string stock_id;
};

#endif /* end of include guard: _STRATEGY_H__ */

