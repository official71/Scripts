#!/usr/bin/env python
#coding=utf-8

import sys
import re
import urllib
from bs4 import BeautifulSoup
from urlparse import urljoin
from collections import defaultdict
from datetime import datetime
import pytz

# since SkySports timezone is UTC, it's important to convert timezone to EST...
SKY_TIMEZONE = 'UTC'
MY_TIMEZONE = 'EST'
utc_tz = pytz.utc
est_tz = pytz.timezone('US/Eastern')

# <h3 class="fixres__header1">March 2017</h3>
def class_fixres__header1(tag):
    return tag.has_attr('class') and tag['class'] == ['fixres__header1']

# <h4 class="fixres__header2">Saturday 18th March</h4>
def class_fixres__header2(tag):
    return tag.has_attr('class') and tag['class'] == ['fixres__header2']

# <div class="fixres__item">...</div>
def class_fixres__item(tag):
    return tag.has_attr('class') and tag['class'] == ['fixres__item']

# <span class="swap-text__target">Arsenal</span>
def class_swaptext__target(tag):
    return tag.has_attr('class') and tag['class'] == ['swap-text__target']

# <span class="matches__date">
#           12:30    </span>
def class_matches__date(tag):
    return tag.has_attr('class') and tag['class'] == ['matches__date']

# remove the ordinal suffix from string
def no_ordianl(s):
    return re.sub(r'(\d)(st|nd|rd|th)', r'\1', s)

def sky_ucl(url, dd_ucl):
    try:
        page = urllib.urlopen(url)
    except:
        print 'Failed to access url: ' + url
        return

    # # list for EPL
    # # key: date
    # # data: list of dict(hour/result/info, home, away, tv, league)
    # dd_ucl = defaultdict(list)

    soup = BeautifulSoup(page, 'lxml')
    curr_tag = soup.find(class_fixres__header1)
    if not curr_tag:
        print 'Failed to find anything on url: ' + url
        return

    type_tag = type(curr_tag)
    while curr_tag:
        if type(curr_tag) == type_tag and class_fixres__header1(curr_tag):
            # March 2017 -> curr_year_utc = 2017
            month_obj = datetime.strptime(curr_tag.text, '%B %Y')
            curr_year_utc = month_obj.year

        # new date UTC
        if type(curr_tag) == type_tag and class_fixres__header2(curr_tag):
            # Saturday 18th March -> curr_month_utc = 3, curr_day_utc = 18
            tmp_obj = datetime.strptime(no_ordianl(curr_tag.text), '%A %d %B')
            curr_month_utc = tmp_obj.month
            curr_day_utc = tmp_obj.day

        if type(curr_tag) == type_tag and class_fixres__item(curr_tag):
            # new defaultdict for a match
            dd = defaultdict(lambda: 'N/A')
            dd['tv'] = "SkySports"
            dd['league'] = "UEFA CL"

            # team names are in targets
            targets = curr_tag.find_all(class_swaptext__target)
            if len(targets) < 2:
                print 'ignore item with less than 2 targets'
                continue
            dd['home'] = targets[0].text
            dd['away'] = targets[1].text

            # match hour, 12:30
            hour = curr_tag.find(class_matches__date)
            
            # convert the UTC time to EST time -> est_t
            s = str(curr_year_utc) + ' ' + str(curr_month_utc) + ' ' + str(curr_day_utc) + ' ' + hour.text.strip()
            utc_t = utc_tz.localize(datetime.strptime(s, '%Y %m %d %H:%M'))
            est_t = utc_t.astimezone(est_tz)

            # now curr_key = %m%d%y to find the list, and match['hour'] = %H:%M EST
            dd['hour'] = datetime.strftime(est_t, '%H:%M '+MY_TIMEZONE)
            curr_key = datetime.strftime(est_t, '%m%d%y')
            
            dd_ucl[curr_key].append(dd)

        curr_tag = curr_tag.next_sibling
