import json
import logging.config
import os
import time
from re import sub
import multiprocessing

import apprise
from bs4 import BeautifulSoup
from chromedriver_py import binary_path
# Load selenium components
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tld import get_fld

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
chrome_options.add_argument("--headless")
chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--incognito')
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


def url_parser(item_url, min, max):
    switcher = {
        'bestbuy.com': bestbuy,
        'amazon.com': amazon,
    }
    parser = switcher.get(get_fld(item_url), lambda x, y, z: logger.info(f'Skipping {x}'))
    parser(item_url, min, max)


def bestbuy(item_link, min, max):
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
        logger.info(f'Item from BestBuy: {title[0].text.strip()} Is Sold?: {is_sold}')
        if not is_sold:
            apobj.notify(
                body=f'Result for {title[0].text.strip()}: {btn[0].text.strip()}',
                title='RTX Notifier',
            )
    except:
        logger.exception(f'Fatal error in Bestbuy parsing: {item_link}')


def amazon(item_link, min, max):
    try:
        driver.get(item_link)
        item_soup = BeautifulSoup(driver.page_source, 'lxml')
        availability = item_soup.select("div#availability > span.a-size-medium.a-color-price")
        title = item_soup.select("span#productTitle")
        is_sold = True
        is_fair = False
        if len(availability) == 0:
            try:
                l = driver.find_element_by_css_selector("div#availability > span.a-size-medium.a-color-success > span.a-declarative > a")
                ActionChains(driver).move_to_element(l).click(l).perform()
                seller_prices = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div#aod-offer-list span.a-price span.a-offscreen")))
                item_soup = BeautifulSoup(driver.page_source, 'lxml')
                seller_prices = item_soup.select("div#aod-offer-list span.a-price span.a-offscreen")
                fair_prices = [x.text for x in seller_prices if min < float(sub(r'[^\d\-.]', '', x.text)) < max]
                is_fair = len(fair_prices) > 0
            except TimeoutException:
                logger.exception(f'Error waiting for: {item_link}')
            except:
                logger.exception(f'Error Parsing: {item_link}')

        logger.info(f'Item from Amazon: {title[0].text.strip()} Is Sold?: {is_sold or not is_fair}')
        if not is_sold and is_fair:
            apobj.notify(
                body=f'Result for {title[0].text.strip()}: {availability}',
                title='RTX Notifier',
            )
    except:
        logger.exception(f'Fatal error in Amazon parsing: {item_link}')


CONFIG_PATH = "config/app_config.json"
logger.info("Starting Scrapper")
driver = webdriver.Chrome(executable_path=binary_path, options=chrome_options)
wait = WebDriverWait(driver, 10)
# p = multiprocessing.Pool(multiprocessing.cpu_count())  # Pool tells how many at a time

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH) as json_file:
        while True:
            config = json.load(json_file)
            for item in config["items"]:
                logger.info(f"Parsing Item: {item['name']} From: {item['url']}")
                driver.get(item["url"])
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'lxml')
                links = soup.select("#trackerContent > #data tr[id] td > a:not(.help)")
                for link in links:
                    try:
                        driver.get(link['href'])
                        url_parser(driver.current_url, float(item["min"]), float(item["max"]))
                    except:
                        logger.exception(f"Fatal error in main loop for: {link['href']}")
                        break
            logger.info("Finished website scrapping")
            time.sleep(180)
else:
    logger.error("No config file found, see here on how to fix this: https://github.com/Hari-Nagarajan/fairgame/wiki/Usage#json-configuration")
    driver.close()
    driver.quit()
    exit(0)


