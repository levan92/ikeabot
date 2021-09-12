import logging
from warnings import warn

from selenium.common.exceptions import WebDriverException

logger = logging.getLogger(__name__)

def get_chrome(webdriver, headless=True, verbose=True, window_size="1080p", user_agent=None):
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    if window_size == '1080p':
        chrome_options.add_argument('window-size=1920,1080')
    if user_agent:
        chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(chrome_options=chrome_options)
    if verbose:
        logger.info(f'Driving with {"headless " if headless else ""}CHROME!')
    return driver

def get_firefox(webdriver, headless=True, verbose=True, window_size="1080p", user_agent=None):
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
        logger.info(f'Driving with {"headless " if headless else ""}FIREFOX!')
    return driver

def get_driver(browser='chrome', headless=True, verbose=True, user_agent=None, webdriver=None):
    if webdriver is None:
        from selenium import webdriver
    browsers = [get_chrome, get_firefox]
    assert browser in ['chrome', 'firefox'],'Given browser not supported'
    if browser == 'firefox':
        browsers = browsers[::-1]

    for get_browser in browsers:
        try:
            driver = get_browser(webdriver, headless=headless, verbose=verbose, user_agent=user_agent)
            return driver
        except WebDriverException as e:
            warn(f'Browser exception:{e}, trying next one.')
            continue

    logger.error('No browsers found.')
    return None
