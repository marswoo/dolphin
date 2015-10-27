#ifndef _UTIL_H__
#define _UTIL_H__

#include <string>
#include <time.h>

using namespace std;

class Util
{
public:
    Util()
    {
        tm open_time;
        tm half_open_time;
        tm half_close_time;
        tm close_time;
        strptime("2013-01-01 09:30:00", "%Y-%m-%d %H:%M:%S", &open_time);
        strptime("2013-01-01 13:30:00", "%Y-%m-%d %H:%M:%S", &half_open_time);
        strptime("2013-01-01 11:30:00", "%Y-%m-%d %H:%M:%S", &half_close_time);
        strptime("2013-01-01 15:00:00", "%Y-%m-%d %H:%M:%S", &close_time);
        time_t open_time_s = mktime(&open_time);
        time_t half_open_time_s = mktime(&half_open_time);
        time_t half_close_time_t = mktime(&half_close_time);
        time_t close_time_s = mktime(&close_time);
    }
    float get_minutes_to_closemarket(time_t now);
    bool if_close_market_today(time_t now);
    void wait_for_half_open(time_t now);

private:
    time_t open_time_s;
    time_t half_open_time_s;
    time_t half_close_time_t;
    time_t close_time_s;

};

#endif /* end of include guard: _UTIL_H__ */

