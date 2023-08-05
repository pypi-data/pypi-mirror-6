from .model import Model


class DeletedEntity(Model):

    def __init__(self, client, data):
        Model.__init__(self, client, data)

    def is_deleted(self):
        """ Always returns `True`
        """
        return True
