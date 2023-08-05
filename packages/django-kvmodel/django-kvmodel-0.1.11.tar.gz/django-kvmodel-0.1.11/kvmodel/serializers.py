"""
the default serializer for the plugin.

it uses json to do the actual work.
"""

import json


def json_serialize(value):
    return json.dumps(value)


def json_deserialize(s):
    return json.loads(s)
