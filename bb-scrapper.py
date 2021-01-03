import datetime
import os
import random
import time
import webbrowser

import requests

links = {"bb_3060FE": [
    "https://www.bestbuy.com/site/nvidia-geforce-rtx-3060-ti-8gb-gddr6-pci-express-4-0-graphics-card-steel-and-black/6439402.p?skuId=6439402", False]
    , "bb_3060MSI": ["https://www.bestbuy.com/site/evga-geforce-rtx-3060-ti-xc-gaming-8gb-gddr6-pci-express-4-0-graphics-card/6444445.p?skuId=6444445", False]
         }

headers = {"User-Agent": "Mozilla/5.0", "cache-control": "max-age=0"}
main_session = requests.Session();


def check():
    print("\n", datetime.datetime.now(), "\n In stock: \n  Best Buy:")
    for key in links:
        check_single_bb(key)
        time.sleep(random.uniform(1, 10))


def check_single_bb(link_url):
    source = main_session.get(links[link_url][0], headers=headers).text
    is_sold_out = source.__contains__(
        "class=\"btn btn-disabled btn-lg btn-block add-to-cart-button\"") or source.__contains__(
        "Coming Soon</button></div></div>") or source.__contains__(" OUT OF STOCK.") or source.__contains__(
        "Temporarily not available")

    if not is_sold_out:
        webbrowser.open(links[link_url][0])
        save_file = open(link_url + ".html", "w")
        save_file.write(source)
        save_file.close()

    links[link_url][1] = is_sold_out
    print("    " + link_url[3:] + ": ", not links[link_url][1])

    if not is_sold_out:
        signal()


def signal():
    while True:
        os.system('say "Yo RTX 3080 on SALE GO go go"')
        time.sleep(0.5)


while True:
    try:
        check()
        time.sleep(120)
    except:
        time.sleep(10)
        pass
