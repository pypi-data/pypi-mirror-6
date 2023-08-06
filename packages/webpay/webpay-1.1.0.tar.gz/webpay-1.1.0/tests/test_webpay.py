from webpay import WebPay
from httmock import HTTMock, urlmatch
import pytest

import tests.helper as helper
import webpay.errors as errors


class TestWebpay:

    def test_request_raises_not_found_with_ja_language(self):
        webpay = WebPay('test_key')
        webpay.accept_language('ja')

        @urlmatch(scheme='https', netloc='api.webpay.jp', path='/v1/customers/cus_eS6dGfa8BeUlbS')
        def mock(url, request):
            assert request.headers['Accept-Language'] == 'ja'
            return helper.response_from_file('errors/not_found_ja.txt', request)

        with pytest.raises(errors.InvalidRequestError) as excinfo:
            with HTTMock(mock):
                webpay.customers.retrieve('cus_eS6dGfa8BeUlbS')
        exc = excinfo.value
        assert exc.args[0].encode('utf-8') == \
            b'\xe8\xa9\xb2\xe5\xbd\x93\xe3\x81\x99\xe3\x82\x8b\xe9\xa1\xa7\xe5\xae\xa2\xe3\x81' + \
            b'\x8c\xe3\x81\x82\xe3\x82\x8a\xe3\x81\xbe\xe3\x81\x9b\xe3\x82\x93: cus_eS6dGfa8BeUlbS'

    def test_request_raises_not_found_with_default_language(self):
        webpay = WebPay('test_key')

        @urlmatch(scheme='https', netloc='api.webpay.jp', path='/v1/charges/foo')
        def mock(url, request):
            assert request.headers['Accept-Language'] == 'en'
            return helper.response_from_file('errors/not_found.txt', request)

        with pytest.raises(errors.InvalidRequestError) as excinfo:
            with HTTMock(mock):
                webpay.charges.retrieve('foo')
        exc = excinfo.value
        assert exc.args[0] == 'No such charge: foo'
