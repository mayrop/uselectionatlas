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


# /RESULTS/statesub.php?off=0&year=2016&elect=0&evt=&f=0&fips=51530&submit=Retrieve

my_map = soup.find(id="pe2016.map")
my_df = pandas.DataFrame(columns=['party', 'count', 'pct', 'state', 'county', 'fips'])
my_file = Path('uselectionatlas.csv')

for state_link in my_map.find_all('area'):
    print(state_link.get('href'))
    
    url = '{}{}'.format(domain, state_link.get('href')) 
    state = slugify(state_link.get('alt'))
    html = request_url(url, state)
    soup = BeautifulSoup(html, 'html.parser')

    options = soup.findAll('select', {'name': 'fips'})

    if len(options) == 0:
        continue
    
    for option in options[0].findAll('option'):
        url = '{}statesub.php?year=2016&fips={}&f=0&off=0&elect=0'
        url = url.format(domain, option.get('value')) 

        county = slugify(option.get_text())
        html = request_url(url, '{}-{}'.format(state, county))

        stats = get_stats(html)
        stats['state'] = state
        stats['county'] = county
        stats['fips'] = option.get('value')

        print('{}-{}'.format(state, county))

        my_df = my_df.append(stats)

my_file.write_text(my_df.to_csv(index=False))