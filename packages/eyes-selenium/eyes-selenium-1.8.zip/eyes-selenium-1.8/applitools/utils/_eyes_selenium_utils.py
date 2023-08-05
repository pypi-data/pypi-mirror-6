"""
Selenium/web driver related utilities.
"""
import time
from ..errors import TestFailedError

_GET_VIEWPORT_HEIGHT_JAVASCRIPT_FOR_NORMAL_BROWSER = 'return window.innerHeight'
_GET_VIEWPORT_WIDTH_JAVASCRIPT_FOR_NORMAL_BROWSER = 'return window.innerWidth'

_DOCUMENT_CLEAR_SCROLL_BARS_JAVASCRIPT = "var doc = document.documentElement; " + \
                                         "var previousOverflow = doc.style.overflow;"
_DOCUMENT_RESET_SCROLL_BARS_JAVASCRIPT = "doc.style.overflow = previousOverflow;"

_DOCUMENT_RETURN_JAVASCRIPT = "return __applitools_result;"

_GET_VIEWPORT_WIDTH_JAVASCRIPT_FOR_BAD_BROWSERS = _DOCUMENT_CLEAR_SCROLL_BARS_JAVASCRIPT + \
                                                  "var __applitools_result = doc.clientWidth;" + \
                                                  _DOCUMENT_RESET_SCROLL_BARS_JAVASCRIPT + \
                                                  _DOCUMENT_RETURN_JAVASCRIPT

_GET_VIEWPORT_HEIGHT_JAVASCRIPT_FOR_BAD_BROWSERS = _DOCUMENT_CLEAR_SCROLL_BARS_JAVASCRIPT + \
                                                   "var __applitools_result = doc.clientHeight;" + \
                                                   _DOCUMENT_RESET_SCROLL_BARS_JAVASCRIPT + \
                                                   _DOCUMENT_RETURN_JAVASCRIPT


def _extract_viewport_width(driver):
    # noinspection PyBroadException
    try:
        return driver.execute_script(_GET_VIEWPORT_WIDTH_JAVASCRIPT_FOR_NORMAL_BROWSER)
    except:
        return driver.execute_script(_GET_VIEWPORT_WIDTH_JAVASCRIPT_FOR_BAD_BROWSERS)


def _extract_viewport_height(driver):
    # noinspection PyBroadException
    try:
        return driver.execute_script(_GET_VIEWPORT_HEIGHT_JAVASCRIPT_FOR_NORMAL_BROWSER)
    except:
        return driver.execute_script(_GET_VIEWPORT_HEIGHT_JAVASCRIPT_FOR_BAD_BROWSERS)


def get_viewport_size(driver):
    # noinspection PyBroadException
    try:
        width = _extract_viewport_width(driver)
        height = _extract_viewport_height(driver)
        return {'width': width, 'height': height}
    except:
        # TODO log('Failed to set viewport size Only window size is available')
        browser_size = driver.get_window_size()
        return {'width': browser_size['width'], 'height': browser_size['height']}


def _verify_size(to_verify, required_size, sleep_time=1, retries=3):
    for retry in range(retries):
        time.sleep(sleep_time)
        current_size = to_verify()
        if current_size['width'] == required_size['width'] \
           and current_size['height'] == required_size['height']:
            return
    error_message = "Failed to setting browser size to %s" % (str(required_size))
    # TODO log
    raise TestFailedError(error_message)


def set_viewport_size(driver, required_size):
    if 'width' not in required_size or 'height' not in required_size:
        raise ValueError('Size must have width & height keys!')
    starting_size = required_size
    driver.set_window_size(required_size['width'], required_size['height'])
    _verify_size(driver.get_window_size, starting_size)
    current_viewport_size = get_viewport_size(driver)
    current_browser_size = driver.get_window_size()
    width_to_set = (2 * current_browser_size['width']) - current_viewport_size['width']
    height_to_set = (2 * current_browser_size['height']) - current_viewport_size['height']
    driver.set_window_size(width_to_set, height_to_set)
    _verify_size(lambda: get_viewport_size(driver), required_size)
