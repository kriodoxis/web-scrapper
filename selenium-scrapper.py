import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
# Load selenium components
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, time
import logging
import logging.config

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, handlers=[logging.StreamHandler()])
logger = logging.getLogger('selenium-scrapper')
chrome_options = Options()  
chrome_options.add_argument("--headless") 
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--incognito')
# Establish chrome driver and go to report site URL
url = "https://nsw2u.com/"
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)
page_source = driver.page_source
driver.close()
soup = BeautifulSoup(page_source, 'lxml')
links = soup.select("a.page-numbers")
logger.info("Starting")
page_numbers = []
all_titles_df = pd.DataFrame(columns=['image', 'title', 'link'])

for link in links:
    try:
        page_numbers.append(int(link.text))
    except ValueError:
        pass

print(page_numbers)