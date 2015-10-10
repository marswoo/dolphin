#ifndef _OBSERVER_H__
#define _OBSERVER_H__

#include <string>
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

    virtual void update(const string& data) const = 0;
};

#endif /* end of include guard: _OBSERVER_H__ */

