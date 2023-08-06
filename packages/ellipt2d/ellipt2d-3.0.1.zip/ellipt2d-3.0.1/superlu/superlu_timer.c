/* 
 * Purpose
 * ======= 
 *	Returns the time in seconds used by the process.
 *
 * Note: the timer function call is machine dependent. Use conditional
 *       compilation to choose the appropriate function.
 *
 */


#ifdef SUN 
/*
 * 	It uses the system call gethrtime(3C), which is accurate to 
 *	nanoseconds. 
*/
#include <sys/time.h>
 
double SuperLU_timer_() {
    return ( (double)gethrtime() / 1e9 );
}

#else

#include <sys/types.h>
#include <time.h>
#ifdef _MSC_VER
#include <sys/timeb.h>
#else
#include <sys/times.h>
#include <sys/time.h>
#endif

#ifndef CLK_TCK
#define CLK_TCK 60
#endif

#ifdef _MSC_VER
double SuperLU_timer_()
{
    struct _timeb use;
    double tmp;
    _ftime(&use);
    tmp = use.time;
    return (double)(tmp);
}
#else
double SuperLU_timer_()
{
    struct tms use;
    double tmp;
    times(&use);
    tmp = use.tms_utime;
    tmp += use.tms_stime;
    return (double)(tmp) / CLK_TCK;
}
#endif

#endif

