import requests
from requests.auth import HTTPBasicAuth
from .test_results import TestResults
from .utils import general_utils


def _parse_response_with_json_data(response):
    response.raise_for_status()
    return response.json()


class AgentConnector(object):
    """
    Provides an API for communication with the Applitools server
    """
    _TIMEOUT = 60 * 5  # Seconds
    _DEFAULT_HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def __init__(self, server_uri, username, password):
        self._endpoint_uri = server_uri.rstrip('/') + '/api/sessions/running'
        self._auth = HTTPBasicAuth(username, password)

    def start_session(self, session_start_info):
        """
        Starts a new running session in the agent. Based on the given parameters,
        this running session will either be linked to an existing session, or to
        a completely new session.

        Args:
            session_start_info (dictionary): The start parameters for the session.
        Returns:
            (dictionary): Represents the current running session.
        Raises:
            see :mod:'requests'
        """
        data = '{"startInfo": %s}' % (general_utils.to_json(session_start_info))
        response = requests.post(self._endpoint_uri, data=data, auth=self._auth, verify=False,
                                 headers=AgentConnector._DEFAULT_HEADERS,
                                 timeout=AgentConnector._TIMEOUT)
        parsed_response = _parse_response_with_json_data(response)
        return dict(session_id=parsed_response['id'], session_url=parsed_response['url'],
                    is_new_session=(response.status_code == requests.codes.created))

    def stop_session(self, running_session, is_aborted, save):
        """
        Stops a running session in the Eyes server.

        Args:
            running_session (RunningSession): The session to stop.
            is_aborted (boolean): Whether the server should mark this session as aborted.
            save (boolean): Whether the session should be automatically saved if it is not aborted.
        Returns:
            TestResults: Test results of the stopped session.
        Raises:
            see :mod:'requests'
        """
        session_uri = "%s/%d" % (self._endpoint_uri, running_session['session_id'])
        params = {'aborted': is_aborted, 'updateBaseline': save}
        response = requests.delete(session_uri, params=params, auth=self._auth, verify=False,
                                   headers=AgentConnector._DEFAULT_HEADERS,
                                   timeout=AgentConnector._TIMEOUT)
        pr = _parse_response_with_json_data(response)
        return TestResults(pr['steps'], pr['matches'], pr['mismatches'], pr['missing'],
                           pr['exactMatches'], pr['strictMatches'], pr['contentMatches'],
                           pr['layoutMatches'], pr['noneMatches'])

    def match_window(self, running_session, match_data):
        """
        Matches the current window to the immediate expected window in the Eyes server. Notice that
        a window might be matched later at the end of the test, even if it was not immediately
        matched in this call.

        Args:
            match_data (dictionary): The data used for matching app output with the expected
            output.
        Returns:
            MatchResult: Whether there was an immediate match or not.
        Raises:
            see :mod:'requests'
        """
        session_uri = "%s/%d" % (self._endpoint_uri, running_session['session_id'])
        data = general_utils.to_json(match_data)
        response = requests.post(session_uri, auth=self._auth, data=data, verify=False,
                                 headers=AgentConnector._DEFAULT_HEADERS,
                                 timeout=AgentConnector._TIMEOUT)
        parsed_response = _parse_response_with_json_data(response)
        return parsed_response['asExpected']
