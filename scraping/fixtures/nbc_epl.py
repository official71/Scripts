#!/usr/bin/env python
#coding=utf-8

import sys
import re
import urllib
from bs4 import BeautifulSoup
from urlparse import urljoin
from collections import defaultdict
from datetime import datetime



def class_shsETZone(tag):
    return tag.has_attr('class') and tag['class'] == ['shsTimezone', 'shsETZone']

def nbc_epl(url_epl, dd_epl):
    try:
        page = urllib.urlopen(url_epl)
    except:
        print('Failed to access url: ' + url_epl)
        return

    # # list for EPL
    # # key: date
    # # data: list of dict(hour/result/info, home, away, tv, league)
    # dd_epl = defaultdict(list)

    soup = BeautifulSoup(page, 'lxml')
    all_tr = soup.find_all("tr")
    curr_key = ""
    for tr in all_tr:
        if not tr.has_attr('class'):
            continue

        # rows of class ['shsTableTtlRow'] contains the date, e.g.
        # <tr class="shsTableTtlRow"><td colspan="6">Saturday, 4 March 2017</td></tr>
        if tr['class'] == ['shsTableTtlRow']:
            # parse 'Saturday, 18 March 2017'
            date_obj = datetime.strptime(tr.text, '%A, %d %B %Y')
            curr_key = datetime.strftime(date_obj, '%m%d%y')
            dd_epl[curr_key] = []

        # rows of class ['shsRow0Row'] and ['shsRow1Row'] contains match info, e.g.
        # <tr class="shsRow0Row">
        # (
        # <td class="shsNamD" nowrap=""><a href="/epl/boxscore.asp?gamecode=2017030410097">3-4</a></td>
        # or
        # <td class="shsNamD" nowrap=""><span class="shsTimezone shsPTZone">10:30 AM PT</span><span class="shsTimezone shsETZone">1:30 PM ET</span>...</td>
        # )
        # <td class="shsNamD"><span class="small_6148 shs_teamLogo"></span><a href="/epl/schedules.asp?team=97">Watford</a></td>
        # <td class="shsNamD"><span class="small_7128 shs_teamLogo"></span><a href="/epl/schedules.asp?team=37">Southampton</a></td>
        # <td class="shsNamD s    hsHideCol">Vicarage Road</td>
        # </tr>
        if tr['class'] == ['shsRow0Row'] or tr['class'] == ['shsRow1Row']:
            # new dictionary
            dd = defaultdict(lambda: 'N/A')
            dd['tv'] = "NBCSports"
            dd['league'] = "EPL"
            
            # match info
            # <a>MATCH RESULT</a> or <span class="shsTimezone shsETZone">MATCH HOUR</span>
            td_info = tr.find("td")
            td_info_a = td_info.find("a")
            td_info_span = td_info.find(class_shsETZone)
            if td_info_a:
                dd['result'] = td_info_a.text
            elif td_info_span:
                try:
                    hr = datetime.strptime(td_info_span.text,'%I:%M %p ET')
                    dd['hour'] = datetime.strftime(hr, '%H:%M')
                except:
                    dd['hour'] = td_info_span.text
            else:
                dd['info'] = td_info.text

            # home team
            # <a>TEAM NAME</a>
            td_home = td_info.find_next("td")
            td_home_a = td_home.find("a")
            if td_home_a:
                dd['home'] = td_home_a.text

            # away team
            # <a>TEAM NAME</a>
            td_away = td_home.find_next("td")
            td_away_a = td_away.find("a")
            if td_away_a:
                dd['away'] = td_away_a.text

            # td_stadium = td_away.find_next("td")
            
            # append dd to list
            dd_epl[curr_key].append(dd)


