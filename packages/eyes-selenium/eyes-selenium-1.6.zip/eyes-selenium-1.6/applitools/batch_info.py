from datetime import datetime, tzinfo, timedelta
from .errors import EyesError


class _UtcTz(tzinfo):
    """A UTC timezone class which is tzinfo compliant."""
    _ZERO = timedelta(0)

    def utcoffset(self, dt):
        return _UtcTz._ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return _UtcTz._ZERO

# Constant representing UTC
_UTC = _UtcTz()


class BatchInfo(object):
    """
    A batch of tests.
    """
    def __init__(self, name=None, started_at=datetime.now(_UTC)):
        self.name = name
        self.started_at = started_at

    def __getstate__(self):
        return dict(name=self.name, startedAt=self.started_at.isoformat())

    # noinspection PyMethodMayBeStatic
    # This function required is required in order for jsonpickle to work on this object.
    def __setstate__(self, state):
        raise EyesError('Cannot create BatchInfo instance from dict!')

    def __str__(self):
        return "%s - %s" % (self.name, self.started_at)