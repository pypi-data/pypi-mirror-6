from webpay.model.token import Token
from .helpers import assertId


class Tokens:

    def __init__(self, webpay):
        self.__client = webpay

    def create(self, **params):
        """Create a token with given params
        """
        if not 'card' in params and 'name' in params:
            params = {'card': params}
        return Token(self.__client, self.__client.post('/tokens', params))

    def retrieve(self, id):
        """Get the token identified by `id`
        """
        assertId(id)
        return Token(self.__client, self.__client.get('/tokens/' + id))
