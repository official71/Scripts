#!/usr/bin/env python
#coding=utf-8

import sys
from collections import defaultdict
from datetime import datetime, timedelta
from nbc_epl import nbc_epl
from sky_epl import sky_epl
from sky_fa import sky_fa
from sky_ucl import sky_ucl
import smtplib
from email.mime.text import MIMEText as MT
from secrets import GMAIL_USER, GMAIL_PASSWD, FROM, TO

# Favorite teams (in lower case)
MY_TEAMS = ['arsenal']
WATCH_TEAMS = ['arsenal', 'chelsea', 'manchester city', 'manchester united', 'liverpool', 'tottenham hotspur']

def send_email(body):
    user = GMAIL_USER
    passwd = GMAIL_PASSWD
    addr_from = FROM
    addr_to = TO if type(TO) is list else [TO]
    subject = 'Fixtures as of ' + datetime.strftime(datetime.today(), '%A, %B %d')
    if subject[-1] == '1':
        subject += 'st'
    elif subject[-1] == '2':
        subject += 'nd'
    elif subject[-1] == '3':
        subject += 'rd'
    else:
        subject += 'th'

    msg = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (addr_from, ', '.join(addr_to), subject, body)
    # print msg

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(user, passwd)
        server.sendmail(addr_from, addr_to, msg)
        server.close()
        print 'successfully sent the email'
    except:
        print 'failed to sent email'


def print_match(match, body):
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

    body += '\n%7s%-12s%-25s  VS      %-25s%-10s%-10s' % (star, info, match['home'], match['away'], match['league'], match['tv'])
    return body



"""
Retrieve fixtures from websites:
1. EPL
   http://scores.nbcsports.msnbc.com/epl/fixtures.asp?month=<m>
   <m> is the month interested in
"""
def get_fixtures():
    body = ""

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
    del_backward = timedelta(0)
    day0 = today + del_backward # from ... days ago
    del_forward = timedelta(14)
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

    # save results
    date = day0
    del_1 = timedelta(1)
    while date != dayX:
        matches = ""
        key = datetime.strftime(date, '%m%d%y')

        # EPL
        for match in dd_epl[key]:
            matches = print_match(match, matches)

        # FA
        for match in dd_fa[key]:
            matches = print_match(match, matches)

        # UCL
        for match in dd_ucl[key]:
            matches = print_match(match, matches)

        if matches:
            if date == today:
                body += '\n\n>-----   ' + datetime.strftime(date, '%a, %d %B %Y') + '   -----< \n'
            else:
                body += '\n\n' + datetime.strftime(date, '%a, %d %B %Y') + '\n'
            body += matches
        # next day
        date += del_1

    return body

def main():
    body = get_fixtures()
    if body:
        send_email(body)
    else:
        print 'empty fixtures, no need to sent email'

if __name__ == "__main__": main()