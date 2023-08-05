from collections import defaultdict
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from ._agent_connector import AgentConnector
from ._match_window_task import MatchWindowTask
from .batch_info import BatchInfo
from .errors import EyesError, NewTestError, TestFailedError
from .test_results import TestResults
from .utils import _eyes_selenium_utils
from applitools import VERSION


class FailureReports(object):
    """
    Failures are either reported immediately when they are detected, or when the test is closed.
    """
    IMMEDIATE = 0
    ON_CLOSE = 1


class MatchLevel(object):
    """
    The extent in which two images match (or are expected to match).
    """
    NONE = "None"
    LAYOUT = "Layout"
    CONTENT = "Content"
    STRICT = "Strict"
    EXACT = "Exact"


class Eyes(object):
    """
    Applitools Selenium Eyes API for python.
    """
    _DEFAULT_MATCH_TIMEOUT = 2
    AGENT_ID = "Eyes.Selenium.Python/%s" % VERSION
    DEFAULT_EYES_SERVER = 'https://eyes.applitools.com'

    api_key = None

    def __init__(self, server_url=DEFAULT_EYES_SERVER, disabled=False):
        """
        Creates a new (possibly disabled) Eyes instance that interacts with the Eyes server.

        Args:
            params (dictionary):
                (Optional) server_url (str): The URL of the Eyes server
                (Optional) disabled (boolean): Whether this Eyes instance is disabled (acts as
                                                mock).
        """
        self._is_disabled = disabled
        if self._is_disabled:
            return
        self._user_inputs = []
        self._running_session = None
        self._agent_connector = AgentConnector(server_url, Eyes.AGENT_ID, Eyes.api_key)
        self._should_get_title = False
        self._driver = None
        self._match_window_task = None
        self._match_level = None
        self._is_open = False
        self._should_match_once_on_timeout = False
        self._app_name = None
        self._test_name = None
        self._viewport_size = None
        self._start_info = None
        self._failure_reports = None
        self.match_timeout = Eyes._DEFAULT_MATCH_TIMEOUT
        self.batch = None  # (BatchInfo)
        self.host_os = None  # (str)
        self.host_app = None  # (str)
        self.save_new_tests = True
        self.save_failed_tests = False
        self.branch_name = None
        self.parent_branch_name = None

    def is_open(self):
        """
        Returns:
            (boolean) True if a session is currently running, False otherwise.
        """
        return self._is_open

    def is_disabled(self):
        """
        Returns:
            (boolean) True if the current Eyes instance is disabled, False otherwise.
        """
        return self._is_disabled

    def get_driver(self):
        """
        Returns:
            (selenium.webdriver.remote.webdriver) The web driver currently used by the Eyes
                                                    instance.
        """
        return self._driver

    def get_match_level(self):
        """
        Returns:
            (match_level) The match level used for the current test (if running), or the next test.
        """
        return self._match_level

    def get_viewport_size(self):
        """
        Returns:
            ({width, height}) The size of the viewport of the application under test (e.g,
                                the browser).
        """
        return self._viewport_size

    def get_failure_reports(self):
        """
        Returns:
            (failure_reports) Whether the current test will report failure immediately or when it
                                is finished.
        """
        return self._failure_reports

    def abort_if_not_closed(self):
        """
        If a test is running, aborts it. Otherwise, does nothing.
        """
        if self.is_disabled():
            return
        if self._running_session:
            # TODO log
            try:
                self._agent_connector.stop_session(self._running_session, True, False)
            except EyesError:
                # TODO log "Failed to abort sever session: %s " % (e)
                pass
            finally:
                self._running_session = None

    def open(self, driver, app_name, test_name, viewport_size=None,
             match_level=MatchLevel.EXACT, failure_reports=FailureReports.ON_CLOSE):
        """
        Starts a test.

        Args:
            params (dictionary):
                app_name (str): The name of the application under test.
                test_name (str): The test name.
                (Optional) viewport_size ({width, height}): The client's viewport size (i.e.,
                                                            the visible part of the document's
                                                            body) or None to allow any viewport
                                                            size.
                (Optional) match_level (match_level): Test-wide match level to use when comparing
                                                        the application outputs with expected
                                                        outputs.
                (Optional) failure_reports (failure_reports): Specifies how detected failures are
                                                                reported.
        Returns:
            An updated web driver
        Raises:
            EyesError
        """
        if self.is_disabled():
            # TODO log
            return driver

        if Eyes.api_key is None:
            raise EyesError('API key is missing! Please set it via Eyes.api_key')

        if (driver is None) or (not isinstance(driver, RemoteWebDriver)):
            raise EyesError('driver must be a valid Selenium web driver object')

        # TODO wrap driver
        self._driver = driver

        if self.is_open():
            self.abort_if_not_closed()
            # TODO log
            raise EyesError('a test is already running')
        self._app_name = app_name
        self._test_name = test_name
        self._viewport_size = viewport_size
        self._failure_reports = failure_reports
        self._match_level = match_level
        self._is_open = True
        return self._driver

    def _assign_viewport_size(self):
        if self._viewport_size:
            _eyes_selenium_utils.set_viewport_size(self._driver, self._viewport_size)
        else:
            self._viewport_size = _eyes_selenium_utils.get_viewport_size(self._driver)

    def _create_start_info(self):
        app_env = {'os': self.host_os, 'hostingApp': self.host_app,
                   'displaySize': self._viewport_size,
                   'inferred': self._get_inferred_environment()}
        self._start_info = {'agentId': Eyes.AGENT_ID, 'appIdOrName': self._app_name,
                            'scenarioIdOrName': self._test_name, 'batchInfo': self.batch,
                            'environment': app_env, 'matchLevel': self._match_level,
                            'verId': None, 'branchName': self.branch_name,
                            'parentBranchName': self.parent_branch_name}

    def _start_session(self):
        self._assign_viewport_size()
        if not self.batch:
            self.batch = BatchInfo()
        self._create_start_info()
        # Actually start the session.
        self._running_session = self._agent_connector.start_session(self._start_info)
        self._should_match_once_on_timeout = self._running_session['is_new_session']

    def _clear_user_inputs(self):
        self._user_inputs = []

    def get_title(self):
        """
        Returns:
            (str) The title of the window of the AUT, or empty string if the title is not
                    available.
        """
        if self._should_get_title:
            # noinspection PyBroadException
            try:
                return self._driver.title
            except:
                self._should_get_title = False
                # Couldn't get title, return empty string.
        return ''

    def _get_inferred_environment(self):
        try:
            user_agent = self._driver.execute_script('return navigator.userAgent')
        except WebDriverException:
            user_agent = None
        if user_agent:
            return "useragent:%s" % user_agent
        return None

    def check_window(self, tag=None):
        """
        Takes a snapshot from the browser using the web driver and matches it with
        the expected output.
        """
        if self.is_disabled():
            return

        if not self.is_open():
            raise EyesError('Eyes not open!')

        if not self._running_session:
            self._start_session()
            self._match_window_task = MatchWindowTask(self, self._agent_connector,
                                                      self._running_session, self._driver,
                                                      self.match_timeout)
        as_expected = self._match_window_task.match_window(tag, self._should_match_once_on_timeout)
        if not as_expected:
            self._should_match_once_on_timeout = True
            if not self._running_session['is_new_session']:
            #         TODO log("mismatch #{ tag ? '' : "(#{tag})" })
                if self._failure_reports == FailureReports.IMMEDIATE:
                    raise TestFailedError("Mismatch found in '%s' of '%s'" %
                                          (self._start_info['scenarioIdOrName'],
                                           self._start_info['appIdOrName']))

    def close(self):
        if self.is_disabled():
            # TODO log
            return

        self._is_open = False

        # If there's no running session, we simply return the default test results.
        if not self._running_session:
            # TODO log
            return TestResults()

        results_url = self._running_session['session_url']
        is_new_session = self._running_session['is_new_session']
        should_save = (is_new_session and self.save_new_tests) or \
                      ((not is_new_session) and self.save_failed_tests)
        results = self._agent_connector.stop_session(self._running_session, False, should_save)
        self._running_session = None
        if is_new_session:
            if should_save:
                instructions = 'Test was automatically accepted. You can review it at %s' % \
                               results_url
            else:
                instructions = "Please approve the new baseline at %s" % results_url
                # TODO log "--- New test ended. %s" % instructions
            message = "'%s' of '%s'. %s" % (self._start_info['scenarioIdOrName'],
                                            self._start_info['appIdOrName'], instructions)
            raise NewTestError(message, results)
        elif 0 < results.mismatches or 0 < results.missing:
            if should_save:
                instructions = "Test was automatically accepted. You can review it at %s" % \
                               results_url
            else:
                instructions = "Test failed. You can review it at %s" % results_url
                # TODO log "--- Failed test ended. %s" % instructions
            message = "'%s' of '%s'. %s" % (self._start_info['scenarioIdOrName'],
                                            self._start_info['appIdOrName'], instructions)
            raise TestFailedError(message, results)
        # Test passed
        return results