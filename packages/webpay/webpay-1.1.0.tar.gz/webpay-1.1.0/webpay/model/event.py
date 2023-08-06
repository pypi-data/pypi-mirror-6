from .helpers import data_to_object_converter
from .model import Model


class Event(Model):

    def __init__(self, client, data):
        Model.__init__(self, client, data)

    def _instantiate_field(self, key, value):
        if key == 'data':
            return EventData(self._client, value)
        else:
            return Model._instantiate_field(self, key, value)


class EventData(Model):

    def __init__(self, client, data):
        Model.__init__(self, client, data)

    def _instantiate_field(self, key, value):
        if key == 'object':
            return data_to_object_converter(self._client)(value)
        else:
            return Model._instantiate_field(self, key, value)
