import base64
from io import BytesIO
import time
from applitools.geometry import Region
from applitools.utils import _viewport_size
# noinspection PyProtectedMember
from .utils._image_utils import png_image_from_bytes


class MatchWindowTask(object):
    """
    Handles matching of output with the expected output (including retry and 'ignore mismatch'
    when needed).
    """
    _MATCH_INTERVAL = 0.5

    def __init__(self, eyes, agent_connector, running_session, driver, max_window_load_time):
        self._eyes = eyes
        self._agent_connector = agent_connector
        self._running_session = running_session
        self._driver = driver
        self._max_window_load_time = max_window_load_time
        self._current_screenshot = None

    def _prepare_match_data(self, region, tag, force_full_page_screenshot, ignore_mismatch):
        title = self._eyes.get_title()
        if force_full_page_screenshot:
            self._current_screenshot = self._driver.get_full_page_screenshot()
            current_screenshot_bytes = BytesIO()
            self._current_screenshot.write(current_screenshot_bytes)
            current_screenshot64 = base64.b64encode(current_screenshot_bytes.getvalue())\
                                         .decode('UTF-8')
        else:
            current_screenshot64 = self._driver.get_screenshot_as_base64()
            self._current_screenshot = png_image_from_bytes(base64.b64decode(current_screenshot64))
        if not region.is_empty():
            self._current_screenshot = self._current_screenshot.get_subimage(region)
            region_png_bytes = BytesIO()
            self._current_screenshot.write(region_png_bytes)
            current_screenshot64 = base64.b64encode(region_png_bytes.getvalue()).decode('UTF-8')

        app_output = {'title': title, 'screenshot64': current_screenshot64}
        # noinspection PyProtectedMember
        return dict(appOutput=app_output, userInputs=self._eyes._user_inputs, tag=tag,
                    ignoreMismatch=ignore_mismatch)

    def _match(self, region, tag, force_full_page_screenshot, ignore_mismatch=False):
        data = self._prepare_match_data(region, tag, force_full_page_screenshot, ignore_mismatch)
        as_expected = self._agent_connector.match_window(self._running_session, data)
        return as_expected

    def _run_once(self, region, tag, viewport_workaround, wait_before_run=None):
        if wait_before_run:
            time.sleep(wait_before_run)
        return self._match(region, tag, viewport_workaround)

    def _run_with_intervals(self, region, tag, force_full_page_screenshot, total_run_time):
        start = time.time()
        match_retry = total_run_time
        while match_retry > 0:
            time.sleep(self._MATCH_INTERVAL)
            if self._match(region, tag, force_full_page_screenshot, True):
                return True
            match_retry -= (time.time() - start)
        # One last try
        return self._match(region, tag, force_full_page_screenshot)

    def match_window(self, region, tag, force_full_page_screenshot, run_once_after_wait=False):
        if not self._max_window_load_time:
            result = self._run_once(region, tag, force_full_page_screenshot)
        elif run_once_after_wait:
            result = self._run_once(region, tag, force_full_page_screenshot,
                                    self._max_window_load_time)
        else:
            result = self._run_with_intervals(region, tag, force_full_page_screenshot,
                                              self._max_window_load_time)
        self._eyes._last_screenshot = self._current_screenshot
        if region.is_empty():
            self._eyes._last_screenshot_bounds = Region(width=self._current_screenshot.width,
                                                        height=self._current_screenshot.height)
        else:
            self._eyes._last_screenshot_bounds = region
        self._eyes._user_inputs = []  # Resetting user inputs
        return result