# coding: utf-8
from webpay import WebPay
from httmock import HTTMock
import pytest

import tests.helper as helper
import webpay.errors as errors


class TestCustomers:

    def test_create(self):
        with HTTMock(helper.mock_api('/customers', 'customers/create.txt')):
            customer = WebPay('test_key').customers.create(
                description='Test Customer from Java',
                email='customer@example.com',
                card={
                    'number': '4242-4242-4242-4242',
                    'exp_month': 12,
                    'exp_year': 2015,
                    'cvc': 123,
                    'name': 'YUUKO SHIONJI'
                },
            )

        assert customer.id == 'cus_39o4Fv82E1et5Xb'
        assert customer.description == 'Test Customer from Java'
        assert customer.active_card.name == 'YUUKO SHIONJI'

    def test_retrieve(self):
        id = 'cus_39o4Fv82E1et5Xb'
        with HTTMock(helper.mock_api('/customers/' + id,
                                     'customers/retrieve.txt')):
            customer = WebPay('test_key').customers.retrieve(id)

        assert customer.id == id
        assert not customer.is_deleted()
        assert customer.active_card.name == 'YUUKO SHIONJI'

    def test_retrieve_without_id(self):
        with pytest.raises(errors.InvalidRequestError) as excinfo:
            WebPay('test_key').customers.retrieve('')
        exc = excinfo.value
        assert exc.type == 'invalid_request_error'
        assert exc.param == 'id'

    def test_retrieve_deleted_customer(self):
        id = 'cus_7GafGMbML8R28Io'
        with HTTMock(helper.mock_api('/customers/' + id,
                                     'customers/retrieve_deleted.txt')):
            customer = WebPay('test_key').customers.retrieve(id)

        assert customer.id == id
        assert customer.is_deleted()

    def test_all(self):
        conds = {'count': 3, 'offset': 0, 'created': {'gt': 1378000000}}
        with HTTMock(helper.mock_api('/customers',
                                     'customers/all.txt',
                                     data=conds)):
            customers = WebPay('test_api').customers.all(**conds)

        assert customers.url == '/v1/customers'
        assert customers.data[0].description == 'Test Customer from Java'
        assert customers.data[0].active_card.name == 'YUUKO SHIONJI'

    def test_save(self):
        id = 'cus_39o4Fv82E1et5Xb'
        with HTTMock(helper.mock_api('/customers/' + id,
                                     'customers/retrieve.txt')):
            customer = WebPay('test_key').customers.retrieve(id)

        old_card = customer.active_card

        expected = {
            'email': 'newmail@example.com',
            'description': 'New description',
            'card': {
                'number': '4242-4242-4242-4242',
                'exp_month': 12,
                'exp_year': 2016,
                'cvc': 123,
                'name': 'YUUKO SHIONJI',
            }}

        customer.email = expected['email']
        customer.description = expected['description']
        customer.new_card = expected['card']

        assert customer.email == 'newmail@example.com'
        assert customer.active_card == old_card

        with HTTMock(helper.mock_api('/customers/' + id,
                                     'customers/update.txt',
                                     data=expected)):
            new_customer = customer.save()

        assert customer.email == 'newmail@example.com'
        assert customer.active_card.exp_year == 2016
        assert new_customer == customer

    def test_save_only_updated_fields(self):
        id = 'cus_39o4Fv82E1et5Xb'
        with HTTMock(helper.mock_api('/customers/' + id,
                                     'customers/retrieve.txt')):
            customer = WebPay('test_key').customers.retrieve(id)

        customer.email = 'newmail@example.com'
        with HTTMock(helper.mock_api('/customers/' + id,
                                     'customers/update.txt',
                                     data={'email': 'newmail@example.com'})):
            customer.save()
        assert customer.email == 'newmail@example.com'

    def test_calling_save_twice_sends_nothing(self):
        id = 'cus_39o4Fv82E1et5Xb'
        with HTTMock(helper.mock_api('/customers/' + id,
                                     'customers/retrieve.txt')):
            customer = WebPay('test_key').customers.retrieve(id)

        expected = {
            'card': {
                'number': '4242-4242-4242-4242',
                'exp_month': 12,
                'exp_year': 2016,
                'cvc': 123,
                'name': 'YUUKO SHIONJI',
            },
            'email': 'newmail@example.com',
            'description': 'New description',
        }

        customer.email = expected['email']
        customer.description = expected['description']
        customer.new_card = expected['card']

        with HTTMock(helper.mock_api('/customers/' + id,
                                     'customers/update.txt',
                                     data=expected)):
            customer.save()

        with HTTMock(helper.mock_api('/customers/' + id,
                                     'customers/update.txt',
                                     data={})):
            customer.save()

    def test_delete(self):
        id = 'cus_39o4Fv82E1et5Xb'
        with HTTMock(helper.mock_api('/customers/' + id,
                                     'customers/retrieve.txt')):
            customer = WebPay('test_key').customers.retrieve(id)

        with HTTMock(helper.mock_api('/customers/' + id,
                                     'customers/delete.txt')):
            assert customer.delete()
