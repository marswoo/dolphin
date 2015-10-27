#include <iostream>
#include <string>
#include "util.h"

using namespace std;

float Util::get_minutes_to_closemarket(time_t now)
{
    struct tm* local_time;
    local_time = localtime(&now);

    char buf[128] = {0};
    strftime(buf, 128, "2013-01-01 %H:%M:%S", local_time);
    tm now_time;
    strptime(buf, "%Y-%m-%d %H:%M:%S", &now_time);
    now = mktime(&now_time);

    if (now < open_time_s) 
        return 241;
    else if (now < half_close_time_t) 
        return (half_close_time_t - now) / 60 + 60 * 2 + 1;
    else if (now < half_open_time_s)
        return 120.5;
    else if (now <= close_time_s)
        return (close_time_s - now) / 60 + 1;
    else
        return -1;
}


bool Util::if_close_market_today(time_t now)
{
    struct tm* local_time;
    local_time = localtime(&now);
    if (local_time->tm_wday == 0 || local_time->tm_wday == 6)
        return true;
    else
        return false;
}

void Util::wait_for_half_open(time_t now)
{
    struct tm* local_time;
    local_time = gmtime(&now);
    if (local_time->tm_hour > 9 || (local_time->tm_hour == 9 && local_time->tm_min > 30))
    {
        time_t t = now + 24 * 3600;
        local_time = gmtime(&t);
    }
    local_time->tm_hour = 9;
    local_time->tm_min = 30;
    local_time->tm_sec = 0;
    time_t tomorrow_s = mktime(local_time);
    cout << "--- wait for open, sleep (s): " << tomorrow_s - now << endl;
    sleep(tomorrow_s - now + 10);
    
    time_t now_n;
    time(&now_n);
    if (if_close_market_today(now_n))
    {
        wait_for_half_open(now_n);
    }
}

//int main()
//{
//    //http://blog.csdn.net/love_gaohz/article/details/6637625
//    Util util;
//    time_t timep;
//    struct tm p;
//    time(&timep);
//    //util.wait_for_half_open(timep);
//    strptime("2013-01-01 14:32:30", "%Y-%m-%d %H:%M:%S", &p);
//    //cout << util.get_minutes_to_closemarket(mktime(&p)) << endl;
//    cout << util.if_close_market_today(timep) << endl;;
//    //p = localtime(&timep);
//    //cout << asctime(localtime(&timep)) << endl;
//    //cout << p->tm_year <<endl;
//    return 0;
//}
