import os

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
# Load selenium components
from selenium import webdriver
from chromedriver_py import binary_path
from bs4 import BeautifulSoup
import apprise
import pandas as pd
from datetime import datetime, time
import logging.config
from tld import get_fld
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
apobj = apprise.Apprise()
# apobj.add('pbul://')
apobj.add('macosx://')
logger = logging.getLogger('selenium-scrapper')
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--incognito')
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


def url_parser(item_url):
    switcher = {
        # 'bestbuy.com': bestbuy,
        'amazon.com': amazon,
    }
    parser = switcher.get(get_fld(item_url), lambda x: logger.info(f'Skipping {x}'))
    parser(item_url)


def bestbuy(item_link):
    try:
        driver.get(item_link)
        # driver.implicitly_wait(5)
        try:
            l = driver.find_element_by_css_selector("div:not(.hidden) > div.country-selection a.us-link")
            ActionChains(driver).move_to_element(l).click(l).perform()
        except NoSuchElementException:
            pass
        item_page_source = driver.page_source
        item_soup = BeautifulSoup(item_page_source, 'lxml')
        btn = item_soup.select("button.btn-lg.add-to-cart-button")
        title = item_soup.select("div.sku-title > h1")
        btn_text = btn[0].text.strip().lower()
        is_sold = "sold out" == btn_text or "coming soon" == btn_text
        logger.info(f'Item: {title[0].text.strip()} Is Sold?: {is_sold}')
        if not is_sold:
            apobj.notify(
                body=f'Result for {title[0].text.strip()}: {btn[0].text.strip()}',
                title='RTX Notifier',
            )
    except:
        logger.exception("Fatal error in Bestbuy parse")


def amazon(item_link):
    try:
        driver.get(item_link)
        item_soup = BeautifulSoup(driver.page_source, 'lxml')
        availability = item_soup.select("div#availability > span.a-size-medium.a-color-price")
        title = item_soup.select("span#productTitle")
        is_sold = True
        logger.info(len(availability))
        if len(availability) > 0:
            logger.info(availability[0].text.strip())
        else:
            try:
                l = driver.find_element_by_css_selector("div#availability > span.a-size-medium.a-color-success > span.a-declarative > a")
                ActionChains(driver).move_to_element(l).click(l).perform()
                seller_prices = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div#aod-offer-list span.a-price span.a-offscreen")))
                item_soup = BeautifulSoup(driver.page_source, 'lxml')
                seller_prices = item_soup.select("div#aod-offer-list span.a-price span.a-offscreen")
                logger.info(seller_prices)
            except:
                logger.exception("Fatal error in Bestbuy parse")

        logger.info(f'Item: {title[0].text.strip()} Is Sold?: {is_sold}')
        if not is_sold:
            apobj.notify(
                body=f'Result for {title[0].text.strip()}: {availability}',
                title='RTX Notifier',
            )
    except:
        logger.exception("Fatal error in Amazon parse")


tracker_url = 'https://www.nowinstock.net/computers/videocards/nvidia/rtx3060ti/'
logger.info("Starting")
driver = webdriver.Chrome(executable_path=binary_path, options=chrome_options)
wait = WebDriverWait(driver, 10)
driver.get(tracker_url)
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')
links = soup.select("#trackerContent > #data tr[id] td > a:not(.help)")
# for link in links:
for link in links:
    try:
        driver.get(link['href'])
        url_parser(driver.current_url)
    except:
        logger.exception("Fatal error in main loop")
        break


driver.close()
driver.quit()
