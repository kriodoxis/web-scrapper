import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import logging
import logging.config


logging.config.fileConfig('logging.conf')
logger = logging.getLogger('simpleExample')
r = requests.get('https://nsw2u.com/')
soup = BeautifulSoup(r.text, 'html.parser')
links = soup.select("a.page-numbers")
logger.info("Starting")
page_numbers = []
all_titles_df = pd.DataFrame(columns=['image', 'title', 'link'])

for link in links:
    try:
        page_numbers.append(int(link.text))
    except ValueError:
        pass

for n in range(1, max(page_numbers) + 1):
    r = requests.get(f'https://nsw2u.com/page/{n}')
    logger.info(f'Scrapping: https://nsw2u.com/page/{n}')
    soup = BeautifulSoup(r.text, 'html.parser')
    links = soup.select("div#primary div.row div.columns.postbox")
    for link in links:
        image = link.select('article img.wp-post-image')[0]['data-src'] if len(link.select('article img.wp-post-image')) > 0 else "_"
        title = link.select('article > a')[0]['title']
        link = link.select('article > a')[0]['href']
        new_row = {
            'image': image,
            'title': title,
            'link': link
        }
        # append row to the dataframe
        all_titles_df = all_titles_df.append(new_row, ignore_index=True)
    time.sleep(5)

# Converting links to html tags
def path_to_image_html(path):
    return f'<img width="180" height="200" src="{path}">'

def path_to_link_html(path):
    return f'<a href="{path}" target="_blank" rel="noopener noreferrer">{path}</a>'

# render dataframe as html
all_titles_df.to_html(f'titles{datetime.now():%Y%m%d%H%M%S%f}.html', escape=False, formatters=dict(image=path_to_image_html,link=path_to_link_html))
