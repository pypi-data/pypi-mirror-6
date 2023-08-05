from webpay.model.charge import Charge
from webpay.model.entity_list import EntityList
from .helpers import assertId


class Charges:

    def __init__(self, webpay):
        self.__client = webpay

    def create(self, **params):
        """Create a charge with given params
        """
        return Charge(self.__client, self.__client.post('/charges', params))

    def retrieve(self, id):
        """Retrieve the charge identified by `id`
        """
        assertId(id)
        return Charge(self.__client, self.__client.get('/charges/' + id))

    def all(self, **params):
        """List charges which meet given conditions
        """
        return EntityList(self.__client, self.__client.get('/charges', params))

    def refund(self, id, amount=None):
        """Refund the charge identified by `id`
        """
        assertId(id)
        return Charge(self.__client, self.__client.post(
            '/charges/%s/refund' % id, {'amount': amount}))

    def capture(self, id, amount=None):
        """Capture the charge identified by `id`.
        It must be not captured.
        """
        assertId(id)
        return Charge(self.__client, self.__client.post(
            '/charges/%s/capture' % id, {'amount': amount}))
