from webpay import WebPay
from httmock import HTTMock
import pytest

import tests.helper as helper
import webpay.errors as errors


class TestErrors:

    def test_request_raises_api_exception(self):
        with pytest.raises(errors.ApiError) as excinfo:
            with HTTMock(helper.mock_api('/charges',
                                         'errors/unknown_api_error.txt')):
                WebPay('test_key').charges.all()
        exc = excinfo.value
        assert exc.__str__() == 'Unknown error occurred'
        assert exc.type == 'api_error'
        assert exc.status == 500

    def test_request_raises_invalid_request(self):
        with pytest.raises(errors.InvalidRequestError) as excinfo:
            with HTTMock(helper.mock_api('/charges',
                                         'errors/bad_request.txt')):
                WebPay('test_key').charges.all()
        exc = excinfo.value
        assert exc.__str__() == 'Missing required param: currency'
        assert exc.type == 'invalid_request_error'
        assert exc.param == 'currency'
        assert exc.status == 400

    def test_request_raises_not_found(self):
        with pytest.raises(errors.InvalidRequestError) as excinfo:
            with HTTMock(helper.mock_api('/charges',
                                         'errors/not_found.txt')):
                WebPay('test_key').charges.all()
        exc = excinfo.value
        assert exc.__str__() == 'No such charge: foo'
        assert exc.type == 'invalid_request_error'
        assert exc.param == 'id'
        assert exc.status == 404

    def test_request_raises_not_found_without_params(self):
        with pytest.raises(errors.InvalidRequestError) as excinfo:
            with HTTMock(helper.mock_api('/charges',
                                         'errors/not_found_url.txt')):
                WebPay('test_key').charges.all()
        exc = excinfo.value
        assert exc.__str__() == 'Unrecognized request URL.'
        assert exc.type == 'invalid_request_error'
        assert exc.status == 404

    def test_request_raises_unauthorized(self):
        with pytest.raises(errors.AuthenticationError) as excinfo:
            with HTTMock(helper.mock_api('/charges',
                                         'errors/unauthorized.txt')):
                WebPay('test_key').charges.all()
        exc = excinfo.value
        assert exc.__str__() == \
            'Invalid API key provided. Check your API key is correct.'
        assert exc.status == 401

    def test_request_raises_card_error(self):
        with pytest.raises(errors.CardError) as excinfo:
            with HTTMock(helper.mock_api('/charges',
                                         'errors/card_error.txt')):
                WebPay('test_key').charges.all()
        exc = excinfo.value
        assert exc.__str__() == 'Your card number is incorrect'
        assert exc.type == 'card_error'
        assert exc.code == 'incorrect_number'
        assert exc.param == 'number'
        assert exc.status == 402

    def test_request_raises_card_error_without_param(self):
        with pytest.raises(errors.CardError) as excinfo:
            with HTTMock(helper.mock_api('/charges',
                                         'errors/card_error_declined.txt')):
                WebPay('test_key').charges.all()
        exc = excinfo.value
        assert exc.__str__() == 'This card cannot be used.'
        assert exc.type == 'card_error'
        assert exc.code == 'card_declined'
        assert exc.param is None
        assert exc.status == 402

    def test_server_not_found(self):
        with pytest.raises(errors.ApiConnectionError) as excinfo:
            with HTTMock(helper.mock_api('/charges',
                                         'errors/not_found.txt')):
                WebPay('test_key', 'http://localhost:123').charges.all()
        exc = excinfo.value
        assert 'Error while requesting API' in exc.__str__()
        assert exc.error_info is None
        assert exc.status is None

    def test_response_json_is_broken(self):
        with pytest.raises(errors.ApiConnectionError) as excinfo:
            with HTTMock(helper.mock_api('/charges',
                                         'errors/broken_json.txt')):
                WebPay('test_key').charges.all()
        exc = excinfo.value
        assert 'Error while parsing response JSON' in exc.__str__()
        assert exc.error_info is None
        assert exc.status is None
