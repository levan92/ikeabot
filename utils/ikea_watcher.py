import json
import logging
from datetime import datetime

from seleniumwire import webdriver
from seleniumwire.utils import decode

from .selenium_utils import get_driver

def not_swedish(char):
    try:
        char.encode(encoding='utf-8').decode('ascii')
        str(char)
    except (UnicodeDecodeError, UnicodeEncodeError):
        return False
    else:
        return True

def englishfy(string):
    eng = [ char for char in string if not_swedish(char) ]
    eng = ''.join(eng)
    return eng

def get_stocks(urls):
    # driver = get_driver(webdriver=webdriver, browser='chrome', headless=True, verbose=True)
    for url in urls:
        get_stock(url)

def req_interceptor(request):
# Block PNG, JPEG and GIF images
    if request.path.endswith(('.png', '.jpg', '.gif')):
        request.abort()

def get_stock(url):
    print('getting driver')
    driver = get_driver(webdriver=webdriver, browser='chrome', headless=True, verbose=True)

    print('getting',url)
    driver.request_interceptor = req_interceptor
    driver.scopes = [
        '.*api.ingka.*'
    ]
    driver.get(url)

    print('parsing reqs')
    for req in driver.requests:
        if req.response and 'api.ingka' in req.url:
            selected = req
            break
    else:
        del driver.requests
        return None
    del driver.requests
    
    body = decode(selected.response.body, 'gzip')
    dic = json.loads(body.decode('utf-8'))

    qtys = []
    avail_delivery  = False
    for outlet in dic['availabilities']:
        try:
            qty = outlet['buyingOption']['cashCarry']['availability']['quantity'] # int
            update_ts = outlet['buyingOption']['cashCarry']['availability']['updateDateTime']
            update_time = datetime.strptime(update_ts, '%Y-%m-%dT%H:%M:%S.%fZ')
            qtys.append(qty)
        except Exception as e:
            pass
        
        try:    
            avail_delivery = outlet['buyingOption']['homeDelivery']['availability']['probability']['thisDay']['colour']['token'] == 'colour-positive'
            update_time = outlet['buyingOption']['homeDelivery']['availability']['probability']['updateDateTime']
        except Exception as e:
            pass
    
    name = englishfy(driver.title).replace('- IKEA', '').strip()
    print(name, qtys, 'avail for delivery' if avail_delivery else 'not avail for delivery')
    del driver
    return name, qtys, avail_delivery

if __name__ == '__main__':

    links = [
        'https://www.ikea.com/sg/en/p/metod-maximera-high-cab-f-oven-w-door-3-drawers-white-maximera-veddinge-white-s89358920/',
        'https://www.ikea.com/sg/en/p/stenared-dining-table-stone-effect-quartz-bamboo-60467887/',
        'https://www.ikea.com/sg/en/p/hemnes-coffee-table-white-stain-light-brown-10413496/',
        'https://www.ikea.com/sg/en/p/malm-chest-of-2-drawers-white-10354642/',
        'https://www.ikea.com/sg/en/p/kolbjoern-cabinet-in-outdoor-beige-50409299/',
        'https://www.ikea.com/sg/en/p/besta-tv-bench-with-doors-white-lappviken-white-s19299137/',
        'https://www.ikea.com/sg/en/p/havsen-sink-bowl-w-visible-front-white-s69253716/',
        ]

    get_stocks(links)