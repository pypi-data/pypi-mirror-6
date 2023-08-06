import webpay.errors


def assertId(id):
    """[Internal]  Assert id is not empty
    """
    if id is None or id.strip() == '':
        raise webpay.errors.InvalidRequestError.empty_id_error()
