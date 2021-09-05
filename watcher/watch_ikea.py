from selenium.common.exceptions import StaleElementReferenceException

from .utils import wait_load, get_driver, ss_elem

BROWSER = 'chrome'
HEADLESS = True
VERBOSE = True
ITEM_LINK = 'https://www.ikea.com/sg/en/p/havsen-sink-bowl-w-visible-front-white-s69253716/'

def get_init_driver():
    return get_driver(browser=BROWSER, headless=HEADLESS, verbose=VERBOSE, user_agent=None)

def get_stocks(item_links, need_ss=False):
    driver = get_driver(browser=BROWSER, headless=HEADLESS, verbose=VERBOSE, user_agent=None)
    res = []
    for item_link in item_links:
        driver.get(item_link)
        name = driver.title

        result = [name]
        try:
            try:
                indicator = wait_load(driver, 'class', 'range-revamp-indicator')
                classname = indicator.get_attribute('class')
            except StaleElementReferenceException:
                indicator = wait_load(driver, 'class', 'range-revamp-indicator')
                classname = indicator.get_attribute('class')
            keyword = classname.split()[-1].split('--')[-1]
            if keyword == 'error':
                print(f'{name} no stock')
                result.append(False)
            elif keyword == 'success':
                print(f'{name} got stock')
                result.append(True)
            else:
                print(f'Unknown keyword {keyword}')
                result.append(None)

            if need_ss:
                try:
                    ss_img = ss_elem(driver, elem=indicator, buffer=400)
                except StaleElementReferenceException:
                    indicator = wait_load(driver, 'class', 'range-revamp-indicator')
                    ss_img = ss_elem(driver, elem=indicator, buffer=400)
                result.append(ss_img)

        except Exception as e:
            if need_ss:
                result.extend([None, None])
            else:
                result.append(None)
            print(f'{e} error scraping for {name}')

        res.append(result)

    return res
