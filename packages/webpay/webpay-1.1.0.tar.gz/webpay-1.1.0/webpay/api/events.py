from webpay.model.event import Event
from webpay.model.entity_list import EntityList
from .helpers import assertId


class Events:

    def __init__(self, webpay):
        self.__client = webpay

    def retrieve(self, id):
        """Get the event identified by `id`
        """
        assertId(id)
        return Event(self.__client, self.__client.get('/events/' + id))

    def all(self, **params):
        """List events which meet given conditions.
        """
        return EntityList(self.__client, self.__client.get('/events', params))
