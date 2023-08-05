import pytz
from datetime import datetime
from .errors import EyesError


class BatchInfo(object):
    """
    A batch of tests.
    """

    def __init__(self, name=None, started_at=datetime.now(pytz.utc)):
        self.name = name
        self.started_at = started_at

    def __getstate__(self):
        return dict(name=self.name, startedAt=self.started_at.isoformat())

    # noinspection PyMethodMayBeStatic
    def __setstate__(self, state):
        raise EyesError('Cannot create BatchInfo instance from dict!')

    def __str__(self):
        return "%s - %s" % (self.name, self.started_at)