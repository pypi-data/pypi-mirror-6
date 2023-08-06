import requests
from applitools import logger
from selenium.webdriver.common.by import By
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