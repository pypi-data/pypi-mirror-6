import webpay.model.account


class Account:

    def __init__(self, webpay):
        self.__client = webpay

    def retrieve(self):
        """Retrieve the account tagged with the current API key
        """
        return (
            webpay.model.account.Account(
                self.__client,
                self.__client.get('/account'))
        )

    def delete_data(self):
        """Delete all test data of this account.
        This is available only when the API key is test private key.
        This operation cannot be undone. Be careful.
        Return true if operation succeeds.
        """
        result = self.__client.delete('/account/data')
        return result['deleted']
