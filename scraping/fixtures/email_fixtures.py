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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from secrets import GMAIL_USER, GMAIL_PASSWD, FROM, TO

# Favorite teams (in lower case)
MY_TEAMS = ['arsenal']
WATCH_TEAMS = ['arsenal', 'chelsea', 'manchester city', 'manchester united', 'liverpool', 'tottenham hotspur']

def send_email(html):
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

    # msg = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (addr_from, ', '.join(addr_to), subject, body)
    # print msg
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = addr_from
    msg['To'] = ', '.join(addr_to)

    text = "Hi,\n\nHere are the fixtures you ordered. Have a wonderful day!\n\n\n"

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(user, passwd)
        server.sendmail(addr_from, addr_to, msg.as_string())
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

def print_match_html(match, html):
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
        star = """&#9734;&#9734;&#9734;"""
    elif home in WATCH_TEAMS and away in WATCH_TEAMS:
        star = """&#9734;&#9734;"""
    elif home in WATCH_TEAMS or away in WATCH_TEAMS:
        star = """&#9734;"""
    else:
        star = ' '

    # team display style
    if home in MY_TEAMS:
        home_style = """;font-weight:bold;color:orangered;font-size:110%%"""
    elif home in WATCH_TEAMS:
        home_style = """;font-weight:bold"""
    else:
        home_style = ''

    if away in MY_TEAMS:
        away_style = """;font-weight:bold;color:orangered;font-size:110%%"""
    elif away in WATCH_TEAMS:
        away_style = """;font-weight:bold"""
    else:
        away_style = ''    

    # background colors
    if match['league'] == 'EPL':
        bg_color = 'powderblue'
    elif match['league'] == 'FA CUP':
        bg_color = 'lemonchiffon'
    elif match['league'] == 'UEFA CL':
        bg_color = 'lightpink'
    elif match['league'] == 'Cap1 CUP':
        bg_color = 'lavender'
    else:
        bg_color = 'gainsboro'

    html += """
    <tr style="background-color:%s;">
        <td style="width:10%%; text-align:right">%s</td>
        <td style="width:14%%">%s</td>
        <td style="width:28%%%s">%s</td>
        <td style="width:28%%%s">%s</td>
        <td style="width:8%%">%s</td>
        <td style="width:12%%">%s</td>
    </tr>
    """ % (bg_color, star, info, home_style, match['home'], away_style, match['away'], match['league'], match['tv'])

    return html



"""
Retrieve fixtures from websites:
1. EPL
   http://scores.nbcsports.msnbc.com/epl/fixtures.asp?month=<m>
   <m> is the month interested in
"""
def get_fixtures():
    plain = ""
    html = """\
    <html>
    <head>
        <style>
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
        }
        th, td {
            padding: 5px;
            text-align: left;
        }
        </style>
    </head>
    <body>
    """
    html_end = """\
    </body>
    </html>
    """

    # anything to send?
    need_send_email = False

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
        matches_plain = ""
        matches_html_tr = ""
        need_send_email = False

        key = datetime.strftime(date, '%m%d%y')

        # EPL
        for match in dd_epl[key]:
            need_send_email = True
            matches_plain = print_match(match, matches_plain)
            matches_html_tr = print_match_html(match, matches_html_tr)

        # FA
        for match in dd_fa[key]:
            need_send_email = True
            matches_plain = print_match(match, matches_plain)
            matches_html_tr = print_match_html(match, matches_html_tr)

        # UCL
        for match in dd_ucl[key]:
            need_send_email = True
            matches_plain = print_match(match, matches_plain)
            matches_html_tr = print_match_html(match, matches_html_tr)

        if need_send_email:
            date_str = datetime.strftime(date, '%a, %d %B %Y')
            if date == today:
                plain += '\n\n>-----   ' + date_str + '   -----< \n'
                date_html = """<h3 style="color:forestgreen;">%s</h3>""" % date_str
            else:
                plain += '\n\n' + date_str + '\n'
                date_html = """<h3>%s</h3>""" % date_str
            
            plain += matches_plain
            html += """\
            %s
            <table style="width: 100%%">%s</table>
            """ % (date_html, matches_html_tr)

        # next day
        date += del_1

    return plain, html + html_end

def main():
    plain, html = get_fixtures()
    if plain:
        send_email(html)
    else:
        print 'empty fixtures, no need to sent email'

if __name__ == "__main__": main()