# coding: utf-8
from webpay import WebPay
from httmock import HTTMock
import pytest

import tests.helper as helper
import webpay.errors as errors


class TestTokens:
    _card_data = {
        'number': '4242-4242-4242-4242',
        'exp_month': 12,
        'exp_year': 2015,
        'cvc': 123,
        'name': 'YUUKO SHIONJI'
    }

    def test_create(self):
        with HTTMock(helper.mock_api('/tokens',
                                     'tokens/create.txt',
                                     data={'card': self._card_data})):
            token = WebPay('test_key').tokens.create(card=self._card_data)

        assert token.id == 'tok_3dw2T20rzekM1Kf'
        assert not token.used
        assert token.card.name == 'YUUKO SHIONJI'

    def test_create_without_card_key(self):
        with HTTMock(helper.mock_api('/tokens',
                                     'tokens/create.txt',
                                     data={'card': self._card_data})):
            token = WebPay('test_key').tokens.create(**self._card_data)

        assert token.id == 'tok_3dw2T20rzekM1Kf'

    def test_retrieve(self):
        id = 'tok_3dw2T20rzekM1Kf'
        with HTTMock(helper.mock_api('/tokens/' + id, 'tokens/retrieve.txt')):
            token = WebPay('test_key').tokens.retrieve(id)

        assert token.id == id
        assert token.card.name == 'YUUKO SHIONJI'

    def test_retrieve_without_id(self):
        with pytest.raises(errors.InvalidRequestError) as excinfo:
            WebPay('test_key').tokens.retrieve('')
        exc = excinfo.value
        assert exc.type == 'invalid_request_error'
        assert exc.param == 'id'
