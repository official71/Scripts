#!/usr/bin/env python
#coding=utf-8

import sys
from collections import defaultdict
from datetime import datetime, timedelta
from nbc_epl import nbc_epl
from sky_epl import sky_epl
from sky_fa import sky_fa
from sky_ucl import sky_ucl

# Favorite teams (in lower case)
MY_TEAMS = ['arsenal']
WATCH_TEAMS = ['arsenal', 'chelsea', 'manchester city', 'manchester united', 'liverpool', 'tottenham hotspur']


def print_match(match):
    # first column hour/result/info?
    info = match['hour']
    if info == 'N/A':
        info = match['result']
        if info == 'N/A':
            info = match['info']

    # check fav teams
    home = match['home'].lower()
    away = match['away'].lower()
    if home in MY_TEAMS or away in MY_TEAMS:
        star = '$$$ '
    elif home in WATCH_TEAMS and away in WATCH_TEAMS:
        star = ' $$ '
    elif home in WATCH_TEAMS or away in WATCH_TEAMS:
        star = '  $ '
    else:
        star = '    '

    print '%7s%-12s%-25s  VS      %-25s%-10s%-10s' % (star, info, match['home'], match['away'], match['league'], match['tv'])



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
    url_nbc_epl_base = "http://scores.nbcsports.msnbc.com/epl/fixtures.asp?month="
    url_sky_epl = "http://www.skysports.com/premier-league-fixtures"
    epl_in_use = "nbc"

    url_sky_fa = "http://www.skysports.com/fa-cup-fixtures"
    fa_in_use = "sky"

    url_sky_ucl = "http://www.skysports.com/champions-league-fixtures"
    ucl_in_use = "sky"

    # data for EPL/FA
    # key: date
    # data: list of dict(hour/result/info, home, away, tv)
    dd_epl = defaultdict(list)
    dd_fa = defaultdict(list)
    dd_ucl = defaultdict(list)

    today = datetime.today()
    del_backward = timedelta(-3)
    day0 = today + del_backward # from ... days ago
    del_forward = timedelta(10)
    dayX = today + del_forward # to ... days later
    month_begin = day0.month
    month_end = dayX.month

    if epl_in_use == "nbc":
        for m in range(month_begin, month_end + 1):
            url_nbc_epl = url_nbc_epl_base + str(m)
            # print url_epl
            nbc_epl(url_nbc_epl, dd_epl)
    elif epl_in_use == "sky":
        sky_epl(url_sky_epl, dd_epl)

    if fa_in_use == "sky":
        sky_fa(url_sky_fa, dd_fa)

    if ucl_in_use == "sky":
        sky_ucl(url_sky_ucl, dd_ucl)

    # show results
    print "\n------------------------------------------ FIXTURES ---------------------------------------------\n"
    date = day0
    del_1 = timedelta(1)
    while date != dayX:
        if date == today:
            print '\n>-----   ' + datetime.strftime(date, '%a, %d %B %Y') + '   -----< \n'
        else:
            print datetime.strftime(date, '%a, %d %B %Y')
            
        key = datetime.strftime(date, '%m%d%y')

        # EPL
        for match in dd_epl[key]:
            print_match(match)

        # FA
        for match in dd_fa[key]:
            print_match(match)

        # UCL
        for match in dd_ucl[key]:
            print_match(match)

        date += del_1

if __name__ == "__main__": main()