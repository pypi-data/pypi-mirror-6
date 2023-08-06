******************
Ravello Python SDK
******************

Overview
========

The Ravello Python SDK is a small SDK for using the Ravello_ service from the
Python_ programming language. The focus is on providing a small set of bindings
that doesn't have any external dependencies. Some features are:

* Supports Python 2.6, 2.7 and 3.3+.
* No dependencies outside the standard library.
* A minimal binding without a client-side object model. Objects and
  represented as simple dictionaries.
* Should work on POSIX, Windows and Mac OSX.

Because there is no client-side object model, you should also read the
`Ravello API Reference`_. All object fields are documented there.

API
===

.. module:: ravello_sdk

The Ravello SDK is implemented by the module :mod:`ravello_sdk`. The module is
safe to be imported into your namespace::

  from ravello_sdk import *

The module has the following contents:

**Exceptions**

.. autoclass:: RavelloError

**Functions**

.. autofunction:: random_luid

.. autofunction:: update_luids

.. autofunction:: application_state

.. autofunction:: new_name

**Classes**

.. autoclass:: RavelloClient
    :members:
    :member-order: bysource


.. _Python: http://www.python.org/
.. _Ravello: http://www.ravellosystems.com/
.. _Ravello API Reference: http://www.ravellosystems.com/developer
