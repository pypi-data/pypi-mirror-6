from .model import Model


class Card(Model):

    def __init__(self, client, data):
        Model.__init__(self, client, data)
