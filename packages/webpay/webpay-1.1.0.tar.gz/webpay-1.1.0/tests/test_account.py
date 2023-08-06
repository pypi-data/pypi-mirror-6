# coding: utf-8
from webpay import WebPay
from httmock import HTTMock

import tests.helper as helper


class TestAccount:

    def test_retrieve(self):
        with HTTMock(helper.mock_api('/account', 'account/retrieve.txt')):
            account = WebPay('test_key').account.retrieve()

        assert account.id == 'acct_2Cmdexb7J2r78rz'
        assert account.email == 'test-me@example.com'
        assert account.currencies_supported == ['jpy']

    def test_delete_data(self):
        with HTTMock(helper.mock_api('/account/data', 'account/delete.txt')):
            assert WebPay('test_key').account.delete_data()
