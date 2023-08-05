# coding: utf-8
from webpay import WebPay
from httmock import HTTMock
import pytest

import tests.helper as helper
import webpay.errors as errors


class TestCharges:

    def test_create(self):
        with HTTMock(helper.mock_api('/charges', 'charges/create.txt')):
            charge = WebPay('test_key').charges.create(
                amount=1000,
                currecy='jpy',
                card={
                    'number': '4242-4242-4242-4242',
                    'exp_month': 12,
                    'exp_year': 2015,
                    'cvc': 123,
                    'name': 'YUUKO SHIONJI'
                },
                description='Test Charge from Java',
            )

        assert charge.id == 'ch_2SS17Oh1r8d2djE'
        assert charge.description == 'Test Charge from Java'
        assert charge.card.name == 'YUUKO SHIONJI'

    def test_retrieve(self):
        id = 'ch_bWp5EG9smcCYeEx'
        with HTTMock(helper.mock_api('/charges/' + id,
                                     'charges/retrieve.txt')):
            charge = WebPay('test_key').charges.retrieve(id)

        assert charge.id == id
        # アイテムの購入
        assert charge.description.encode('utf-8') == \
            b'\xe3\x82\xa2\xe3\x82\xa4\xe3\x83\x86\xe3\x83\xa0\xe3\x81\xae' + \
            b'\xe8\xb3\xbc\xe5\x85\xa5'
        assert charge.card.name == 'KEI KUBO'

    def test_retrieve_without_id(self):
        with pytest.raises(errors.InvalidRequestError) as excinfo:
            WebPay('test_key').charges.retrieve('')
        exc = excinfo.value
        assert exc.type == 'invalid_request_error'
        assert exc.param == 'id'

    def test_all(self):
        with HTTMock(helper.mock_api('/charges', 'charges/all.txt')):
            charges = WebPay('test_api').charges \
                .all(count=3, offset=0, created={'gt': 1378000000})

        assert charges.url == '/v1/charges'
        assert charges.data[0].description == 'Test Charge from Java'
        assert charges.data[0].card.name == 'KEI KUBO'
        assert charges._client == charges.data[0]._client

    def test_refund(self):
        id = 'ch_bWp5EG9smcCYeEx'
        with HTTMock(helper.mock_api('/charges/' + id,
                                     'charges/retrieve.txt')):
            charge = WebPay('test_key').charges.retrieve(id)
        with HTTMock(helper.mock_api('/charges/%s/refund' % id,
                                     'charges/refund.txt')):
            charge.refund(400)

        assert charge.refunded
        assert charge.amount_refunded == 400
        assert charge._data['amount_refunded'] == 400

    def test_refund_without_amount(self):
        id = 'ch_bWp5EG9smcCYeEx'
        with HTTMock(helper.mock_api('/charges/' + id,
                                     'charges/retrieve.txt')):
            charge = WebPay('test_key').charges.retrieve(id)
        with HTTMock(helper.mock_api('/charges/%s/refund' % id,
                                     'charges/refund.txt')):
            charge.refund()

        assert charge.refunded
        assert charge.amount_refunded == 400

    def test_capture(self):
        id = 'ch_2X01NDedxdrRcA3'
        with HTTMock(helper.mock_api('/charges/' + id,
                                     'charges/retrieve_not_captured.txt')):
            charge = WebPay('test_key').charges.retrieve(id)
        with HTTMock(helper.mock_api('/charges/%s/capture' % id,
                                     'charges/capture.txt')):
            charge.capture(1000)

        assert charge.captured
        assert charge.paid
        assert charge.amount == 1000
