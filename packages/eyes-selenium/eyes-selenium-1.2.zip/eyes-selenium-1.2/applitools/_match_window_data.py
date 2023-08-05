from .errors import EyesError


class MatchWindowData(object):
    """
    Encapsulates the data to be sent to the agent on a "matchWindow" command.
    """
    def __init__(self, app_output, user_inputs=None, tag=None, ignore_mismatch=False):
        if not user_inputs:
            user_inputs = []
        self.app_output = app_output
        self.user_inputs = user_inputs
        self.tag = tag
        self.ignore_mismatch = ignore_mismatch

    def __getstate__(self):
        return dict(appOutput=self.app_output, userInputs=self.user_inputs, tag=self.tag,
                    ignoreMismatch=self.ignore_mismatch)

    # noinspection PyMethodMayBeStatic
    def __setstate__(self):
        raise EyesError("Cannot create instance from dict!")
