import time


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

    def _prepare_match_data(self, tag, ignore_mismatch):
        title = self._eyes.get_title()
        screenshot64 = self._driver.get_screenshot_as_base64()
        app_output = {'title': title, 'screenshot64': screenshot64}
        # TODO get user inputs
        return dict(appOutput=app_output, userInputs=[], tag=tag, ignoreMismatch=ignore_mismatch)

    def _match(self, tag, ignore_mismatch=False):
        data = self._prepare_match_data(tag, ignore_mismatch)
        as_expected = self._agent_connector.match_window(self._running_session, data)
        return as_expected

    def _run_once(self, tag, wait_before_run=None):
        if wait_before_run:
            time.sleep(wait_before_run)
        return self._match(tag)

    def _run_with_intervals(self, tag, total_run_time):
        start = time.time()
        match_retry = total_run_time
        while match_retry > 0:
            time.sleep(self._MATCH_INTERVAL)
            if self._match(tag, True):
                return True
            match_retry -= (time.time() - start)
        # One last try
        return self._match(tag)

    def match_window(self, tag, run_once_after_wait=False):
        if not self._max_window_load_time:
            result = self._run_once(tag)
        elif run_once_after_wait:
            result = self._run_once(tag, self._max_window_load_time)
        else:
            result = self._run_with_intervals(tag, self._max_window_load_time)
        # TODO clear eyes.user_inputs?
        return result