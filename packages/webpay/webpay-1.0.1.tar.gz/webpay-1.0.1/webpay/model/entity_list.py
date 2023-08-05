from .helpers import data_to_object_converter
from .model import Model


class EntityList(Model):

    """List of the same entities.
    This list is the return value of ``all()``.
    """

    def __init__(self, client, data):
        Model.__init__(self, client, data)

    def _instantiate_field(self, key, value):
        if key == 'data':
            return list(map(data_to_object_converter(self._client), value))
        else:
            return Model._instantiate_field(self, key, value)
