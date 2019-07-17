from bs4 import BeautifulSoup
from helpers import *
from slugify import slugify
import pandas
import re
import time
import urllib.parse as urlparse
from pathlib import Path

domain = 'https://uselectionatlas.org/RESULTS/'
url = '{}national.php?year=2016&off=0&elect=0&f=0'.format(domain)
html = request_url(url)

soup = BeautifulSoup(html, 'html.parser')


my_map = soup.find(id="pe2016.map")
my_df = pandas.DataFrame(columns=['party', 'count', 'pct', 'state', 'county', 'fips'])
my_file = Path('uselectionatlas.csv')

for state_link in my_map.find_all('area'):
    print(state_link.get('href'))
    
    url = '{}{}'.format(domain, state_link.get('href')) 
    state = slugify(state_link.get('alt'))
    html = request_url(url, state)
    soup = BeautifulSoup(html, 'html.parser')

    state_map = soup.find(id="year_select")

    for county_link in state_map.find_all('area'):
        url = '{}{}'.format(domain, county_link.get('href')) 
        county = slugify(county_link.get('alt'))
        html = request_url(url, '{}-{}'.format(state, county))

        par = urlparse.parse_qs(urlparse.urlparse(url).query)

        stats = get_stats(html)
        stats['state'] = state
        stats['county'] = county
        stats['fips'] = par['fips'][0]

        print('{}-{}'.format(state, county))

        my_df = my_df.append(stats)

my_file.write_text(my_df.to_csv(index=False))