# coding: utf-8
from webpay import WebPay
from httmock import HTTMock
import pytest

import tests.helper as helper
import webpay.errors as errors


class TestEvents:

    def test_retrieve(self):
        id = 'evt_39o9oUevb5NCeM1'
        with HTTMock(helper.mock_api('/events/' + id, 'events/retrieve.txt')):
            event = WebPay('test_key').events.retrieve(id)

        assert event.id == id
        assert event.data.object.email == 'customer@example.com'

    def test_retrieve_without_id(self):
        with pytest.raises(errors.InvalidRequestError) as excinfo:
            WebPay('test_key').events.retrieve('')
        exc = excinfo.value
        assert exc.type == 'invalid_request_error'
        assert exc.param == 'id'

    def test_all(self):
        conds = {'type': '*.created'}
        with HTTMock(helper.mock_api('/events',
                                     'events/all_with_type.txt',
                                     data=conds)):
            events = WebPay('test_api').events.all(**conds)

        assert events.url == '/v1/events'
        assert events.data[0].type == 'customer.created'
        assert events.data[0].data.object.active_card.name == 'YUUKO SHIONJI'
