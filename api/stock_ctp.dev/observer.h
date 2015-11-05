#ifndef _OBSERVER_H__
#define _OBSERVER_H__

#include <string>
#include "trader.h"
#include "ThostFtdcMdApiSSE.h"
#include "ThostFtdcUserApiStructSSE.h"

using namespace std;

class Observer
{
public:
    Observer()
    {
    }

    ~Observer()
    {
    }

    virtual void update(const string& data, Trader* trader)
    {
    }
};

#endif /* end of include guard: _OBSERVER_H__ */

