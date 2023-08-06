from .model import Model


class Account(Model):

    def __init__(self, client, data):
        Model.__init__(self, client, data)
