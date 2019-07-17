from bs4 import BeautifulSoup
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
import time
import pandas
import re

def cache_file(url, name=''):
    if not name:
        name = '{}'.format(hashlib.sha224(url.encode()).hexdigest())

    path = './cache/{}.txt'.format(name)
    return Path(path)


def _get_from_cache(url, name=''):
    file = cache_file(url, name)

    if file.is_file():
        return file.read_text()


def _get_from_remote(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
                      'AppleWebKit/537.11 (KHTML, like Gecko) '
                      'Chrome/23.0.1271.64 Safari/537.11',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive'}

    req = Request(url=url, headers=headers)
    
    return urlopen(req).read()  


def request_url(url, name='', wait=1):
    content = _get_from_cache(url, name)

    if not content:
        content = _get_from_remote(url)
        cache_file(url, name).write_bytes(content)
        time.sleep(wait)

    return content


def get_stats(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.findAll('table', {"class": "result"})[0]
    df = pandas.DataFrame(columns=['party', 'count', 'pct'])

    for row in table.find('tbody').findAll('tr'):
        if row.find_all(text=re.compile(r'Other', re.I)):
            party = 'Other'
            count = row.findAll('td', {"style": "text-align:right"})[0].get_text()
            pct = row.findAll('td', {"style": "text-align:right"})[1].get_text()

        else:
            party = row.findAll('td', {"class": "name"})[0].get_text()
            count = row.findAll('td', {"class": "num"})[0].get_text()
            pct = row.findAll('td', {"class": "num"})[1].get_text()

        df = df.append({
            'party': party.strip(),
            'count': count.replace(',', '').strip(),
            'pct': pct.replace('%', '').strip()
        }, ignore_index=True)

    return df