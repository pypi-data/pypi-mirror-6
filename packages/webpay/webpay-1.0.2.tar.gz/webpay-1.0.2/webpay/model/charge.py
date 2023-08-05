from webpay.model.card import Card
from .model import Model


class Charge(Model):

    def __init__(self, client, data):
        Model.__init__(self, client, data)

    def _instantiate_field(self, key, value):
        if key == 'card':
            return Card(self._client, value)
        else:
            return Model._instantiate_field(self, key, value)

    def refund(self, amount=None):
        """Refund this charge.

        Arguments:
        - `amount`: amount to refund.
          If `amount` is not given or `None`, refund all.
          If `amount` is less than this charge's amount, refund partially.
        """
        self._update_attributes(self._client.charges.refund(self.id, amount))

    def capture(self, amount=None):
        """Capture this charge.
        This charge should be uncaptured (created with capture=false) and not
        yet expired.

        Arguments:
        - `amount`: amount to capture.
          If `amount` is not given or `None`, use `this.amount`.
        """
        self._update_attributes(self._client.charges.capture(self.id, amount))
