#!/usr/bin/env python
#coding=utf-8

import sys
from collections import defaultdict
from datetime import datetime, timedelta
from nbc_epl import nbc_epl

def output(star, info, home, away, tv, league):
    if star:
        s = ' * '
    else:
        s = '   '
    print '%3s%-12s%-25s  VS      %-25s%-10s%-10s' % (s, info, home, away, league, tv)

"""
Retrieve fixtures from websites:
1. EPL
   http://scores.nbcsports.msnbc.com/epl/fixtures.asp?month=<m>
   <m> is the month interested in
"""
def main():
    usage = "fixtures.py [league]"
    if len(sys.argv) > 2:
        print 'Too many arguments. Usage: ' + usage
        exit(1)
    elif len(sys.argv) == 2:
        league = sys.argv[1]

    # URL
    url_epl_base = "http://scores.nbcsports.msnbc.com/epl/fixtures.asp?month="

    # Favorite teams
    fav_teams = ['arsenal']

    # data for EPL
    # key: date
    # data: list of dict(hour/result/info, home, away, tv)
    dd_epl = defaultdict(list)

    today = datetime.today()
    del_backward = timedelta(-3)
    day0 = today + del_backward # from ... days ago
    del_forward = timedelta(14)
    dayX = today + del_forward # to ... days later
    month_begin = day0.month
    month_end = dayX.month

    for m in range(month_begin, month_end + 1):
        url_epl = url_epl_base + str(m)
        # print url_epl
        nbc_epl(url_epl, dd_epl)


    # show results
    print "\n------------------------------------------ FIXTURES ---------------------------------------------\n"
    date = day0
    del_1 = timedelta(1)
    while date != dayX:
        if date == today:
            print '\n--------------------------'
        print datetime.strftime(date, '%a, %d %B %Y')
        key = datetime.strftime(date, '%m%d%y')
        for match in dd_epl[key]:
            # first column hour/result/info?
            s = match['hour']
            if s == 'N/A':
                s = match['result']
                if s == 'N/A':
                    s = match['info']
            # check fav teams
            star = match['home'].lower() in fav_teams or match['away'].lower() in fav_teams

            output(star, s, match['home'], match['away'], match['tv'], match['league'])
        if date == today:
            print '\n--------------------------'
        date += del_1

if __name__ == "__main__": main()