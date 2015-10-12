#include <iostream>
#include "datafeeder.h"

//register a listener
void Strategy::update(const string& stock_data)
{
    cout << this->stock_id << " data: " << stock_data << endl;
}
