import json


class Model:

    def __init__(self, client, data):
        self._client = client
        self._data = data

        for k, v in data.items():
            self.__dict__[k] = self._instantiate_field(k, v)

    def _instantiate_field(self, key, value):
        return value

    def __str__(self):
        t = type(self)
        json_str = json.dumps(self._data, indent=4, sort_keys=True)
        return '<%s.%s> %s' % (t.__module__, t.__name__, json_str)

    def _update_attributes(self, new_object):
        data = new_object._data
        self._data = data
        for k, v in data.items():
            self.__dict__[k] = self._instantiate_field(k, v)
