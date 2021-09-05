from warnings import warn

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium import webdriver

SELECTOR_METHOD = {'css': By.CSS_SELECTOR,
                   'xpath': By.XPATH,
                   'id': By.ID,
                   'class': By.CLASS_NAME,
                   }

def wait_load(this_driver, selector_method, selector_str, desc='', timeout=10, verbose=True):
    assert selector_method in SELECTOR_METHOD
    selector = SELECTOR_METHOD[selector_method]
    if desc != '':
        desc = f'{desc} '
    if verbose:
        print(f'{desc}loading..')
    try:
        selected = WebDriverWait(this_driver, timeout).until(EC.presence_of_element_located((selector, selector_str)))
        if verbose:
            print (f"{desc}loaded!")
    except TimeoutException:
        print (f"{desc}loading took too much time!")
        selected = None
    return selected

def wait_load_visibility(this_driver, selector_method, selector_str, desc='', timeout=10, verbose=True):
    assert selector_method in SELECTOR_METHOD
    selector = SELECTOR_METHOD[selector_method]
    if desc != '':
        desc = f'{desc} '
    if verbose:
        print(f'{desc}loading..')
    try:
        selected = WebDriverWait(this_driver, timeout).until(EC.visibility_of_element_located((selector, selector_str)))
        if verbose:
            print (f"{desc}loaded!")
    except TimeoutException:
        print (f"{desc}loading took too much time!")
        selected = None
    return selected


def get_chrome(headless=True, verbose=True, window_size="1080p", user_agent=None):
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    if window_size == '1080p':
        chrome_options.add_argument('window-size=1920,1080')
    if user_agent:
        chrome_options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    if verbose:
        print(f'Driving with {"headless " if headless else ""}CHROME!')
    return driver

def get_firefox(headless=True, verbose=True, window_size="1080p", user_agent=None):
    firefoxOptions = webdriver.FirefoxOptions()
    if headless:
        firefoxOptions.set_headless()
    if window_size == '1080p':
        firefoxOptions.add_argument("--width=1920")
        firefoxOptions.add_argument("--height=1080")
    if user_agent:
        firefoxOptions.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Firefox(firefox_options=firefoxOptions)
    if verbose:
        print(f'Driving with {"headless " if headless else ""}FIREFOX!')
    return driver

def get_driver(browser='chrome', headless=True, verbose=True, user_agent=None):
    browsers = [get_chrome, get_firefox]
    assert browser in ['chrome', 'firefox'],'Given browser not supported'
    if browser == 'firefox':
        browsers = browsers[::-1]

    for get_browser in browsers:
        try:
            driver = get_browser(headless=headless, verbose=verbose, user_agent=user_agent)
            return driver
        except WebDriverException as e:
            warn(f'Browser exception:{e}, trying next one.')
            continue

    print('No browsers found.')
    return None

from datetime import timedelta
def round_time(ts, round_minutes=0):
    diff = round_minutes - ts.minute
    ts += timedelta(minutes=diff)
    if diff <= 0 :
        ts += timedelta(hours=1)
    ts = ts.replace(second=0, microsecond=0)
    return ts


import os
import platform
def say(words='hello'):
    plat = platform.system()
    try:
        if plat == 'Linux':
            os.system(f'spd-say "{words}"')
        elif plat == 'Darwin':
            os.system(f'say -v Samantha "{words}"')
        else:
            return
    except Exception as e:
        print(f'say exception: {e}')
        return 

import io
from PIL import Image
def ss_elem(driver, elem=None, buffer=400):
    ss = driver.get_screenshot_as_png()
    ss_img = Image.open(io.BytesIO(ss))
    iw, ih = ss_img.size
    if elem:
        location = elem.location
        size = elem.size
        left = max(0, location['x'] - buffer)
        top = max(0, location['y'] - buffer)
        right = min(iw-1, location['x'] + size['width'] + buffer)
        bottom = min(ih-1, location['y'] + size['height'] + buffer)
        ss_img = ss_img.crop((left, top, right, bottom))
    output = io.BytesIO()
    ss_img.convert('RGB').save(output, format='JPEG')
    return output.getvalue()

