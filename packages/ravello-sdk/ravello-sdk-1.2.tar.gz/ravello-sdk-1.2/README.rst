Ravello Python SDK
==================

This is a small SDK for accessing the Ravello_ API in Python

Installation
------------

Installation from the Python Package Index::

 $ pip install ravell-sdk

Installation from source::

 $ python setup.py install

Running the tests
-----------------

Run the unit tests on your current Python version::

 $ python tests/unit.py

Run the integration tests on your current Python version::

 $ cp test.conf.in test.conf
 # edit test.conf and follow the comments
 $ python tests/integration.py

Run all tests on all supported Python versions::

 $ tox

Example
-------

The following shows a small example of how to use the SDK::

 from ravello_sdk import *
 client = RavelloClient()
 client.login('username', 'Passw0rd')
 for app in client.get_applications():
     print('Found Application: {0}'.format(app['name']))

Documentation
-------------

The documentation is available on readthedocs_.

Source Code
-----------

The source code for this project is on Github_.

License
-------

The Ravello Python SDK is licensed under the Apache 2.0 license.

.. _Ravello: http://www.ravellosystems.com
.. _readthedocs: http://ravello-sdk.readthedocs.org/en/latest
.. _Github: https://github.com/ravello/python-sdk
