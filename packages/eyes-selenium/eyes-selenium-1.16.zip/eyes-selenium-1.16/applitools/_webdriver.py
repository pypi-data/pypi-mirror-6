import base64
import requests
import time
from applitools import logger
from selenium.webdriver.common.by import By
from applitools.geometry import Point
from applitools.utils import _viewport_size, _image_utils
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

    def __init__(self, element, eyes, driver):
        self.element = element
        self._eyes = eyes
        self._driver = driver
        # Since we might be inside a frame, the actual location of the element might be offsetted
        self._absolute_location_offset = driver.current_offset
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
        # noinspection PyUnresolvedReferences
        location = self.location
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
            result = EyesWebElement(result, self._eyes, self._driver)
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
                updated_results.append(EyesWebElement(element, self._eyes, self._driver))
            results = updated_results
        return results

    def click(self):
        control = self.bounds
        control.left += self._absolute_location_offset['x']
        control.top += self._absolute_location_offset['y']
        offset = control.middle_offset
        self._eyes.add_mouse_trigger('click', control, offset)
        logger.info("Click (%s %s)" % (control, offset))
        self.element.click()

    def send_keys(self, *value):
        control = self.bounds
        control.left += self._absolute_location_offset['x']
        control.top += self._absolute_location_offset['y']
        text = u''.join(map(str, value))
        self._eyes.add_text_trigger(control, text)
        logger.info("Text (%s %s)" % (control, text))
        self.element.send_keys(*value)


class _EyesSwitchTo(object):
    """
    Wraps a selenium "SwitchTo" object, so we can keep track of switching between frames.
    """
    _READONLY_PROPERTIES = ['alert', 'active_element']

    def __init__(self, driver, switch_to):
        self._switch_to = switch_to
        self._driver = driver
        general_utils.create_proxy_interface(self, switch_to, self._READONLY_PROPERTIES)

    def frame(self, frame_reference):
        # Find the frame's location and add it to the current driver offset
        if isinstance(frame_reference, str):
            frame_element = self._driver.find_element_by_name(frame_reference)
        elif isinstance(frame_reference, int):
            frame_elements_list = self._driver.find_elements_by_css_selector('frame, iframe')
            frame_element = frame_elements_list[frame_reference]
        else:
            # It must be a WebElement
            frame_element = frame_reference
        # Calling the underlying "SwitchTo" object
        # noinspection PyProtectedMember
        self._driver._switched_to_frame(frame_reference, frame_element)
        return self._switch_to.frame(frame_reference)

    def default_content(self):
        # This call resets the driver's current frame location
        # noinspection PyProtectedMember
        self._driver._switched_to_frame(None)
        return self._switch_to.default_content()


class EyesWebDriver(object):
    """
    A wrapper for selenium web driver which creates wrapped elements, and notifies us about
    events / actions.
    """
    # Properties require special handling since even testing if they're callable "activates"
    # them, which makes copying them automatically a problem.
    _READONLY_PROPERTIES = ['application_cache', 'current_url', 'current_window_handle',
                            'desired_capabilities', 'log_types', 'name', 'page_source', 'title',
                            'window_handles', 'switch_to']
    _SETABLE_PROPERTIES = ['orientation']

    _MAX_SCROLL_BAR_SIZE = 20  # This should pretty much cover all scroll bars.

    def __init__(self, driver, eyes):
        self.driver = driver
        self._eyes = eyes
        # List of frames the user switched to, and the current offset, so we can properly
        # calculate elements' coordinates
        self._frames = []
        self._current_offset = {'x': 0, 'y': 0}
        driver_takes_screenshot = driver.capabilities.get('takesScreenshot', False)
        if driver_takes_screenshot:
            self._screenshot_taker = None
        else:
            logger.debug('Driver can\'t take screenshots, using our own screenshot taker.')
            # noinspection PyProtectedMember
            self._screenshot_taker = _ScreenshotTaker(driver.command_executor._url,
                                                      driver.session_id)

        # Creating the rest of the driver interface by simply forwarding it to the underlying
        # driver.
        general_utils.create_proxy_interface(self, driver,
                                             self._READONLY_PROPERTIES + self._SETABLE_PROPERTIES)

        for attr in self._READONLY_PROPERTIES:
            if not hasattr(self.__class__, attr):
                setattr(self.__class__, attr, general_utils.create_proxy_property(attr,
                                                                                  self.driver))
        for attr in self._SETABLE_PROPERTIES:
            if not hasattr(self.__class__, attr):
                setattr(self.__class__, attr, general_utils.create_proxy_property(attr, self.driver,
                                                                                  True))

    def get(self, url):
        # We're loading a new page, so the frame location resets
        self._switched_to_frame(None)
        return self.driver.get(url)

    def find_element(self, by=By.ID, value=None):
        """
        Returns a WebElement denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        result = self.driver.find_element(by, value)
        # Wrap the element.
        if result:
            result = EyesWebElement(result, self._eyes, self)
        return result

    def find_elements(self, by=By.ID, value=None):
        """
        Returns a list of web elements denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        results = self.driver.find_elements(by, value)
        # Wrap all returned elements.
        if results:
            updated_results = []
            for element in results:
                updated_results.append(EyesWebElement(element, self._eyes, self))
            results = updated_results
        return results

    def find_element_by_id(self, id_):
        """Finds an element by id.

        :Args:
         - id\_ - The id of the element to be found.

        :Usage:
            driver.find_element_by_id('foo')
        """
        return self.find_element(by=By.ID, value=id_)

    def find_elements_by_id(self, id_):
        """
        Finds multiple elements by id.

        :Args:
         - id\_ - The id of the elements to be found.

        :Usage:
            driver.find_element_by_id('foo')
        """
        return self.find_elements(by=By.ID, value=id_)

    def find_element_by_xpath(self, xpath):
        """
        Finds an element by xpath.

        :Args:
         - xpath - The xpath locator of the element to find.

        :Usage:
            driver.find_element_by_xpath('//div/td[1]')
        """
        return self.find_element(by=By.XPATH, value=xpath)

    def find_elements_by_xpath(self, xpath):
        """
        Finds multiple elements by xpath.

        :Args:
         - xpath - The xpath locator of the elements to be found.

        :Usage:
            driver.find_elements_by_xpath("//div[contains(@class, 'foo')]")
        """
        return self.find_elements(by=By.XPATH, value=xpath)

    def find_element_by_link_text(self, link_text):
        """
        Finds an element by link text.

        :Args:
         - link_text: The text of the element to be found.

        :Usage:
            driver.find_element_by_link_text('Sign In')
        """
        return self.find_element(by=By.LINK_TEXT, value=link_text)

    def find_elements_by_link_text(self, text):
        """
        Finds elements by link text.

        :Args:
         - link_text: The text of the elements to be found.

        :Usage:
            driver.find_elements_by_link_text('Sign In')
        """
        return self.find_elements(by=By.LINK_TEXT, value=text)

    def find_element_by_partial_link_text(self, link_text):
        """
        Finds an element by a partial match of its link text.

        :Args:
         - link_text: The text of the element to partially match on.

        :Usage:
            driver.find_element_by_partial_link_text('Sign')
        """
        return self.find_element(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_elements_by_partial_link_text(self, link_text):
        """
        Finds elements by a partial match of their link text.

        :Args:
         - link_text: The text of the element to partial match on.

        :Usage:
            driver.find_element_by_partial_link_text('Sign')
        """
        return self.find_elements(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_element_by_name(self, name):
        """
        Finds an element by name.

        :Args:
         - name: The name of the element to find.

        :Usage:
            driver.find_element_by_name('foo')
        """
        return self.find_element(by=By.NAME, value=name)

    def find_elements_by_name(self, name):
        """
        Finds elements by name.

        :Args:
         - name: The name of the elements to find.

        :Usage:
            driver.find_elements_by_name('foo')
        """
        return self.find_elements(by=By.NAME, value=name)

    def find_element_by_tag_name(self, name):
        """
        Finds an element by tag name.

        :Args:
         - name: The tag name of the element to find.

        :Usage:
            driver.find_element_by_tag_name('foo')
        """
        return self.find_element(by=By.TAG_NAME, value=name)

    def find_elements_by_tag_name(self, name):
        """
        Finds elements by tag name.

        :Args:
         - name: The tag name the use when finding elements.

        :Usage:
            driver.find_elements_by_tag_name('foo')
        """
        return self.find_elements(by=By.TAG_NAME, value=name)

    def find_element_by_class_name(self, name):
        """
        Finds an element by class name.

        :Args:
         - name: The class name of the element to find.

        :Usage:
            driver.find_element_by_class_name('foo')
        """
        return self.find_element(by=By.CLASS_NAME, value=name)

    def find_elements_by_class_name(self, name):
        """
        Finds elements by class name.

        :Args:
         - name: The class name of the elements to find.

        :Usage:
            driver.find_elements_by_class_name('foo')
        """
        return self.find_elements(by=By.CLASS_NAME, value=name)

    def find_element_by_css_selector(self, css_selector):
        """
        Finds an element by css selector.

        :Args:
         - css_selector: The css selector to use when finding elements.

        :Usage:
            driver.find_element_by_css_selector('#foo')
        """
        return self.find_element(by=By.CSS_SELECTOR, value=css_selector)

    def find_elements_by_css_selector(self, css_selector):
        """
        Finds elements by css selector.

        :Args:
         - css_selector: The css selector to use when finding elements.

        :Usage:
            driver.find_elements_by_css_selector('.foo')
        """
        return self.find_elements(by=By.CSS_SELECTOR, value=css_selector)

    def get_screenshot_as_base64(self):
        """
        Gets the screenshot of the current window as a base64 encoded string
           which is useful in embedded images in HTML.

        :Usage:
            driver.get_screenshot_as_base64()
        """
        if self._screenshot_taker is None:
            screenshot = self.driver.get_screenshot_as_base64()
        else:
            screenshot = self._screenshot_taker.get_screenshot_as_base64()
        return screenshot

    def extract_full_page_width(self):
        # noinspection PyUnresolvedReferences
        return self.execute_script("return document.documentElement.scrollWidth")

    def extract_full_page_height(self):
        # noinspection PyUnresolvedReferences
        return self.execute_script("return document.documentElement.scrollHeight")

    def get_current_scroll_position(self):
        """
        Extracts the current scroll position from the browser.
        """
        # noinspection PyUnresolvedReferences
        x = self.execute_script("return window.scrollX")
        # noinspection PyUnresolvedReferences
        y = self.execute_script("return window.scrollY")
        return Point(x, y)

    def scroll_to(self, p):
        """
        Commands the browser to scroll to a given position using javascript.
        """
        # noinspection PyUnresolvedReferences
        self.execute_script("window.scrollTo({0}, {1})".format(p.x, p.y))

    def get_entire_page_size(self):
        """
        Extracts the size of the current page from the browser using Javascript.
        """
        return {'width': self.extract_full_page_width(),
                'height': self.extract_full_page_height()}

    def get_full_page_screenshot(self):
        logger.info('get_full_page_screenshot()')
        frames = []
        if self._frames:
            frames = self._frames[:]
            logger.debug("Current context inside frames, switching to the default content")
            self.switch_to.default_content()

        original_scroll_position = self.get_current_scroll_position()

        self.scroll_to(Point(0, 0))

        entire_page_size = self.get_entire_page_size()

        # Starting with the screenshot at 0,0
        screenshot64 = self.get_screenshot_as_base64()
        screenshot = _image_utils.png_image_from_bytes(base64.b64decode(screenshot64))
        # If the screenshot is the same size as the page size, no stitching is required.
        if (screenshot.width >= self.extract_full_page_width()) and \
                (screenshot.height >= self.extract_full_page_height()):
            return screenshot

        # We the fact that we might use a "smaller" viewport size than the actual viewport size
        # doesn't matter, since we'll take a screenshot of the entire page.
        viewport_size = {'width': _viewport_size.extract_viewport_width(self),
                         'height': _viewport_size.extract_viewport_height(self) -
                                   EyesWebDriver._MAX_SCROLL_BAR_SIZE}

        logger.debug("Total size: {0}, Viewport: {1}".format(entire_page_size, viewport_size))

        screenshot_parts = Region(0, 0, entire_page_size['width'], entire_page_size['height']) \
            .get_sub_regions(viewport_size)

        # Starting with the screenshot at 0,0
        stitched_image = screenshot

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

        # switching back to the frames we were in
        for frame_reference in frames:
            self.driver.switch_to.frame(frame_reference)

        return stitched_image

    def _switched_to_frame(self, frame_reference, frame_element=None):
        """
        Updates the current webdriver the a switch is made to a frame element
        """
        if frame_element is not None:
            self._frames.append(frame_reference)
            frame_location = frame_element.location
            self._current_offset['x'] += frame_location['x']
            self._current_offset['y'] += frame_location['y']
        else:
            # We moved out of the frames
            self._frames = []
            self._current_offset = {'x': 0, 'y': 0}

    @property
    def switch_to(self):
        return _EyesSwitchTo(self, self.driver.switch_to)

    @property
    def current_offset(self):
        """
        The current offset of elements (e.g., due to switching into frames)
        """
        return self._current_offset
