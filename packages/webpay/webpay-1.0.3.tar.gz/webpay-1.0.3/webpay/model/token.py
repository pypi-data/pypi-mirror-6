from webpay.model.card import Card
from .model import Model


class Token(Model):

    def __init__(self, client, data):
        Model.__init__(self, client, data)

    def _instantiate_field(self, key, value):
        if key == 'card':
            return Card(self._client, value)
        else:
            return Model._instantiate_field(self, key, value)
