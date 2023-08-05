"""
General purpose utilities.
"""
import json
import jsonpickle


def to_json(obj):
    """
    Returns an object's json representation based on jsonpickle.
    """
    return jsonpickle.encode(obj, unpicklable=False)


def public_state_to_json(obj):
    """
    Returns an object's json representation, without(!) its private variables.
    DO NOT USE! This method has a problem with "datetime" objects (which have no __dict__
    attribute).
    """
    def get_public_state(o):
        return {key: value for key, value in o.__dict__.items()
                if not callable(value) and not key.startswith('_')}

    return json.dumps(obj, default=lambda o: get_public_state(o), indent=4)


