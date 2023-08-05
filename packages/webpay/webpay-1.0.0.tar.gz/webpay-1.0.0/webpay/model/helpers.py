import webpay.model as model
import webpay.errors


def data_to_object_converter(client):
    """Return a function to convert entity dict data to entity object
    """

    def converter(data):
        object = data['object']
        if object == 'charge':
            return model.charge.Charge(client, data)
        elif object == 'customer':
            return model.customer.Customer(client, data)
        elif object == 'event':
            return model.event.Event(client, data)
        elif object == 'token':
            return model.token.Token(client, data)
        elif object == 'account':
            return model.account.Account(client, data)
        else:
            raise webpay.errors.APIConnectionError(
                'Unknown object type ' + object, None, None, None)

    return converter
