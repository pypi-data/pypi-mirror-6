webpay-python
====================================

.. image:: https://badge.fury.io/py/webpay.png
    :target: http://badge.fury.io/py/webpay

.. image:: https://api.travis-ci.org/webpay/webpay-python.png
    :target: http://travis-ci.org/webpay/webpay-python

webpay-python is a client library for python of `WebPay <https://webpay.jp>`_.

Requirements
====================================

CPython 2.6, 2.7, 3.2, 3.3

Installation
====================================

::

    $ pip install webpay

Usage
====================================

.. code:: python

    from webpay import WebPay
    webpay = WebPay('YOUR_TEST_SECRET_KEY')

    webpay.charges.create(
      amount=400,
      currency="jpy",
      card={
        'number': '4242-4242-4242-4242',
        'exp_month': '11',
        'exp_year': '2014',
        'cvc': '123',
        'name': 'FOO BAR'
      }
      )

See `Python API document <https://webpay.jp/docs/api/python>`_ on WebPay
official page for more details.

Dependencies
====================================

-   `kennethreitz/requests <https://github.com/kennethreitz/requests>`_

Development
====================================

Testing
-----------------------------------

::

    $ pip install -r dev-requirements.txt
    $ py.test

License
====================================

`The MIT License (MIT) <http://opensource.org/licenses/mit-license.html>`_

Copyright (c) 2013 WebPay.
