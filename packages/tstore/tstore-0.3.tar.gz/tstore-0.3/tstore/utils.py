"""
tstore utilities
"""

import json


class JSONEncoder(json.JSONEncoder):
    """
    Adds support for datetime.datetime objects.

    >>> json.dumps({'a': datetime.datetime(2013, 12, 10)}, cls=JSONEncoder)
    '{"a": "2013-12-10T00:00:00Z"}'
    >>> json.dumps({'a': datetime.time()}, cls=JSONEncoder)
    Traceback (most recent call last):
        ...
    TypeError: datetime.time(0, 0) is not JSON serializable
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            return json.JSONEncoder.default(self, obj)


