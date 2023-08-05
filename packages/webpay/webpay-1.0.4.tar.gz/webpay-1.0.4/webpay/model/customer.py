from webpay.model.card import Card
from .model import Model


class Customer(Model):

    def __init__(self, client, data):
        Model.__init__(self, client, data)

    def _instantiate_field(self, key, value):
        if key == 'active_card':
            return Card(self._client, value)
        else:
            return Model._instantiate_field(self, key, value)

    def is_deleted(self):
        """ Always returns `False`
        """
        return False

    def save(self):
        """Save updated data to WebPay server.

        Following fields are updated:
        - `email`
        - `description`
        - `new_card`: `active_card` is a Card object, `new_card` is a dict.
          Setting new card info as a dict to `active_card` has no effect.
        """

        params = {}
        if hasattr(self, 'email') and self._data['email'] != self.email:
            params['email'] = self.email
        if hasattr(self, 'description') \
                and self._data['description'] != self.description:
            params['description'] = self.description
        if hasattr(self, 'new_card') and self.new_card is not None:
            params['card'] = self.new_card
            self.new_card = None

        self._update_attributes(self._client.customers.save(self.id, **params))
        return self

    def delete(self):
        """Delete this customer from WebPay
        """
        return self._client.customers.delete(self.id)
