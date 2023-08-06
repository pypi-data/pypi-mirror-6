import base64
import requests
import time
from applitools import logger
from selenium.webdriver.common.by import By
from applitools.geometry import Point
from applitools.utils import _viewport_size, _image_utils
from applitools.utils._image_utils import PngImage
from .geometry import Region
from .utils import general_utils


class _ScreenshotTaker(object):
    """
    A wrapper class for taking screenshots from a remote web driver.
    """

    def __init__(self, driver_server_uri, driver_session_id):
        self._endpoint_uri = "%s/session/%s/screenshot" % (driver_server_uri.rstrip('/'),
                                                           driver_session_id)

    def get_screenshot_as_base64(self):
        """
        Returns a base64 encoded screenshot from the web driver.
        """
        response = requests.get(self._endpoint_uri)
        response.raise_for_status()
        return response.json()['value']


class EyesWebElement(object):
    """
    A wrapper for selenium web element. This enables eyes to be notified about actions/events for
    this element.
    """

    _METHODS_TO_REPLACE = ['find_element', 'find_elements']

    # Properties require special handling since even testing if they're callable "activates"
    # them, which makes copying them automatically a problem.
    _READONLY_PROPERTIES = ['tag_name', 'text', 'location_once_scrolled_into_view', 'size',
                            'location', 'parent', 'id']

    def __init__(self, element, eyes):
        self.element = element
        self._eyes = eyes

        # Replacing implementation of the underlying driver with ours. We'll put the original
        # methods back before destruction.
        self._original_methods = {}
        for method_name in self._METHODS_TO_REPLACE:
            self._original_methods[method_name] = getattr(element, method_name)
            setattr(element, method_name, getattr(self, method_name))

        # Copies the web element's interface
        general_utils.create_proxy_interface(self, element, self._READONLY_PROPERTIES)
        # Setting properties
        for attr in self._READONLY_PROPERTIES:
            setattr(self.__class__, attr, general_utils.create_proxy_property(attr, self.element))

    @property
    def bounds(self):
        location = self.element.location
        left, top = location['x'], location['y']
        width = height = 0  # Default

        # noinspection PyBroadException
        try:
            size = self.element.size
            width, height = size['width'], size['height']
        except:
            # Not implemented on all platforms.
            pass
        if left < 0:
            left, width = 0, max(0, width + left)
        if top < 0:
            top, height = 0, max(0, height + top)
        return Region(left, top, width, height)

    def find_element(self, by=By.ID, value=None):
        """
        Returns a WebElement denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        result = self._original_methods['find_element'](by, value)
        # Wrap the element.
        if result:
            result = EyesWebElement(result, self._eyes)
        return result

    def find_elements(self, by=By.ID, value=None):
        """
        Returns a list of web elements denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        results = self._original_methods['find_elements'](by, value)
        # Wrap all returned elements.
        if results:
            updated_results = []
            for element in results:
                updated_results.append(EyesWebElement(element, self._eyes))
            results = updated_results
        return results

    def click(self):
        control = self.bounds
        offset = control.middle_offset
        self._eyes.add_mouse_trigger('click', control, offset)
        logger.info("Click (%s %s)" % (control, offset))
        self.element.click()

    def send_keys(self, *value):
        control = self.bounds
        text = u''.join(map(str, value))
        self._eyes.add_text_trigger(control, text)
        logger.info("Text (%s %s)" % (control, text))
        self.element.send_keys(*value)


class EyesWebDriver(object):
    """
    A wrapper for selenium web driver which creates wrapped elements, and notifies us about
    events / actions.
    """
    # Methods to be replaced in the underlying driver with our implementation. This must be done,
    # since the underlying driver methods might thse methods (so it's not enough to just create
    # them on the wrapping web driver.
    _METHODS_TO_REPLACE = ['find_element', 'find_elements', 'get_screenshot_as_base64']

    # Properties require special handling since even testing if they're callable "activates"
    # them, which makes copying them automatically a problem.
    _READONLY_PROPERTIES = ['application_cache', 'current_url', 'current_window_handle',
                            'desired_capabilities', 'log_types', 'name', 'page_source', 'title',
                            'window_handles']
    _SETABLE_PROPERTIES = ['orientation']

    def __init__(self, driver, eyes):
        self.driver = driver
        self._eyes = eyes

        driver_takes_screenshot = driver.capabilities.get('takesScreenshot', False)
        if driver_takes_screenshot:
            self._screenshot_taker = None
        else:
            logger.debug('Driver can\'t take screenshots, using our own screenshot taker.')
            # noinspection PyProtectedMember
            self._screenshot_taker = _ScreenshotTaker(driver.command_executor._url,
                                                      driver.session_id)

        # Replacing implementation of the underlying driver with ours. We'll put the original
        # methods back before destruction.
        self._original_methods = {}
        for method_name in self._METHODS_TO_REPLACE:
            self._original_methods[method_name] = getattr(driver, method_name)
            setattr(driver, method_name, getattr(self, method_name))

        # Creating the rest of the driver interface by simply forwarding it to the underlying
        # driver.
        general_utils.create_proxy_interface(self, driver,
                                             self._READONLY_PROPERTIES + self._SETABLE_PROPERTIES)
        # Forwarding properties
        for attr in self._READONLY_PROPERTIES:
            setattr(self.__class__, attr, general_utils.create_proxy_property(attr, self.driver))
        for attr in self._SETABLE_PROPERTIES:
            setattr(self.__class__, attr, general_utils.create_proxy_property(attr, self.driver,
                                                                              True))

    def _reset_driver(self):
        # Before our driver object is "destroyed" we return the original implementation to the
        # underlying driver.
        try:
            for name, method in self._original_methods.items():
                setattr(self.driver, name, method)
        finally:
            self._original_methods = {}

    def find_element(self, by=By.ID, value=None):
        """
        Returns a WebElement denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        result = self._original_methods['find_element'](by, value)
        # Wrap the element.
        if result:
            result = EyesWebElement(result, self._eyes)
        return result

    def find_elements(self, by=By.ID, value=None):
        """
        Returns a list of web elements denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        results = self._original_methods['find_elements'](by, value)
        # Wrap all returned elements.
        if results:
            updated_results = []
            for element in results:
                updated_results.append(EyesWebElement(element, self._eyes))
            results = updated_results
        return results

    def get_screenshot_as_base64(self):
        """
        Gets the screenshot of the current window as a base64 encoded string
           which is useful in embedded images in HTML.

        :Usage:
            driver.get_screenshot_as_base64()
        """
        if self._screenshot_taker is None:
            screenshot = self._original_methods['get_screenshot_as_base64']()
        else:
            screenshot = self._screenshot_taker.get_screenshot_as_base64()
        return screenshot

    def extract_full_page_width(self):
        return self.execute_script("return document.documentElement.scrollWidth")

    def extract_full_page_height(self):
        return self.execute_script("return document.documentElement.scrollHeight")

    def get_current_scroll_position(self):
        """
        Extracts the current scroll position from the browser.
        """
        x = self.execute_script("return window.scrollX")
        y = self.execute_script("return window.scrollY")
        return Point(x, y)

    def scroll_to(self, p):
        """
        Commands the browser to scroll to a given position using javascript.
        """
        self.execute_script("window.scrollTo({0}, {1})".format(p.x, p.y))

    def get_entire_page_size(self):
        """
        Extracts the size of the current page from the browser using Javascript.
        """
        return {'width': self.extract_full_page_width(),
                'height': self.extract_full_page_height()}

    def get_full_page_screenshot(self):
        logger.info('get_full_page_screenshot()')

        original_scroll_position = self.get_current_scroll_position()

        self.scroll_to(Point(0, 0))

        entire_page_size = self.get_entire_page_size()
        # We specifically use these to get the viewport without the scrollbars.
        viewport_size_no_scrollbars = _viewport_size.extract_viewport_size_no_scrollbars(self)
        viewport_size_with_scrollbars = {'width': _viewport_size.extract_viewport_width(self),
                                         'height': _viewport_size.extract_viewport_height(self)}
        right_scrollbar_size = viewport_size_with_scrollbars['width'] - \
            viewport_size_no_scrollbars['width']
        bottom_scrollbar_size = viewport_size_with_scrollbars['height'] - \
            viewport_size_no_scrollbars['height']
        logger.debug("Total size: {0}, Viewport: {1}".format(entire_page_size,
                                                             viewport_size_no_scrollbars))

        screenshot_parts = Region(0, 0, entire_page_size['width'], entire_page_size['height'])\
            .get_sub_regions(viewport_size_no_scrollbars)

        # Starting with the screenshot at 0,0
        screenshot64 = self.get_screenshot_as_base64()
        stitched_image = _image_utils.png_image_from_bytes(base64.b64decode(screenshot64))

        for part in screenshot_parts:
            # Since we already took the screenshot for 0,0
            if part.left == 0 and part.top == 0:
                logger.debug('Skipping screenshot for 0,0 (already taken)')
                continue
            logger.debug("Taking screenshot for {0}".format(part))
            self.scroll_to(Point(part.left, part.top))
            # Give it time to scroll
            time.sleep(0.1)
            # Since screen size might cause the scroll to reach only part of the way
            current_scroll_position = self.get_current_scroll_position()
            logger.debug("Scrolled To ({0},{1})".format(current_scroll_position.x,
                                                        current_scroll_position.y))
            screenshot64 = self.get_screenshot_as_base64()
            screenshot = _image_utils.png_image_from_bytes(base64.b64decode(screenshot64))
            stitched_image.paste(current_scroll_position.x, current_scroll_position.y,
                                 screenshot.pixels)

        # Returning the user to the original position
        self.scroll_to(original_scroll_position)
        # Removing scroll bars
        stitched_image.remove_columns(stitched_image.width - right_scrollbar_size,
                                      right_scrollbar_size)
        stitched_image.remove_rows(stitched_image.height - bottom_scrollbar_size,
                                   bottom_scrollbar_size)
        return stitched_image
