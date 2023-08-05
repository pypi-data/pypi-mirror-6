from webpay.model.customer import Customer
from webpay.model.deleted_entity import DeletedEntity
from webpay.model.entity_list import EntityList
from .helpers import assertId


class Customers:

    def __init__(self, webpay):
        self.__client = webpay

    def create(self, **params):
        """Create a customer with given params
        """
        return Customer(self.__client, self.__client.post('/customers',
                                                          params))

    def retrieve(self, id):
        """Get the customer identified by `id`
        """
        assertId(id)
        response = self.__client.get('/customers/' + id)
        if 'deleted' in response:
            return DeletedEntity(self.__client, response)
        else:
            return Customer(self.__client, response)

    def all(self, **params):
        """List customers which meet given conditions.
        """
        return EntityList(self.__client, self.__client.get('/customers',
                                                           params))

    def save(self, id, **params):
        """Update attributes of the customer identified by `id`
        """
        assertId(id)
        return (
            Customer(
                self.__client,
                self.__client.post(
                    '/customers/' +
                    id,
                    params))
        )

    def delete(self, id):
        """Delete the customer identified by `id`
        Return `True` if it is successfully deleted.
        """
        assertId(id)
        return self.__client.delete('/customers/' + id)['deleted']
