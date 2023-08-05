from .errors import EyesError


class AppEnvironment(object):
    """
    The environment in which the application under test is executing.
    """

    def __init__(self, os=None, hosting_app=None, display_size=None, inferred=None):
        """
        Args:
            os (str): The operating system on which the test is run.
            hosting_app (str): The application running the tested application (e.g. Firefox
                                browser running the tested website).
            display_size ({width, height}): The width and height of the AUT.
            inferred (str): A string representing the app environment. The inferred string is in the
                             format "source:info" where source is either "useragent" or "pos".
                             Information associated with a "useragent" source is a valid browser
                             user agent string. Information associated with a "pos" source is a
                             string of the format "process-name;os-name" where "process-name" is the
                             name of the main module of the executed process and "os-name" is the OS
                             name.
        """
        self.os = os
        self.hosting_app = hosting_app
        self.display_size = display_size
        self.inferred = inferred

    def __getstate__(self):
        return dict(os=self.os, hostingApp=self.hosting_app, displaySize=self.display_size,
                    inferred=self.inferred)

    def __setstate__(self, state):
        raise EyesError("Cannot create instance from dict!")