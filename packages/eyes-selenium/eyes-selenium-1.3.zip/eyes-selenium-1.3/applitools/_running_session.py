class RunningSession(object):
    """
    Encapsulates data for the session currently running in the Eyes server.
    """

    def __init__(self, session_id, session_url, is_new_session):
        self.session_id = session_id
        self.session_url = session_url
        self.is_new_session = is_new_session
