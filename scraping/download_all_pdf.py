#!/usr/bin/env python
#coding=utf-8

import sys
import re
import urllib
from bs4 import BeautifulSoup
from urlparse import urljoin

"""
Scraping and download all pdf files from input website
"""
usage = "download_all_pdf.py <url>"
if len(sys.argv) != 2:
    print 'Error arguments. Usage: ' + usage
    exit(1)

url = sys.argv[1]
try:
    page = urllib.urlopen(url)
except:
    print('Failed to access url: ' + url)

soup = BeautifulSoup(page, 'lxml')
all_links = soup.find_all("a")
for link in all_links:
    href_url = link.get("href")
    if re.match(r'.+\.pdf$', href_url):
        # extract the pdf url
        pdf_url = urljoin(url, href_url)
        # print pdf_url

        fname = pdf_url.rsplit('/', 1)[1]
        # print fname

        print 'Downloading file :' + pdf_url + '  ... ',
        urllib.urlretrieve(pdf_url, fname)
        print 'Done'

        # hx = url.split('name=')[1].replace('%', '')
        # uch = bytearray.fromhex(hx).decode('utf-8')
        # print uch + ',' ,

        # # go deeper extract the evaluation
        # try:
        #     pg = urllib2.urlopen('http://www.ximizi.com/' + url)
        # except:
        #     print('N/A')

        # sp = BeautifulSoup(pg, 'lxml')
        # al = sp.find_all("font", color="#009900")
        # if not al:
        #     print('N/A')
        # for l in al:
        #     print l.text