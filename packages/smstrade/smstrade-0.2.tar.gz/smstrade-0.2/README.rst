About smstrade
==============

Smstrade is a `Python <http://www.python.org/>`_ library that can be used to
send SMS via the service of `smstrade.eu <http://www.smstrade.eu>`_.

The http(s) API is documented at
http://www.smstrade.eu/pdf/SMS-Gateway_HTTP_API_v2_en.pdf.

Installation
------------

You can either install smstrade from the `Python Package Index`_ PyPI or from
the `Git repository`_.

To install from PyPI you may use `pip`_::

    pip install smstrade

To install from Git you need to clone the repository and run setup.py::

    git clone https://git.gitorious.org/python-smstrade/python-smstrade.git
    cd python-smstrade
    python setup.py develop

.. note:: Be aware that you need write access to you Python installation to
    perform the last step above. You may also use a `virtualenv`_ environment
    to run a sandboxed version of smstrade.

.. _Python Package Index: https://pypi.python.org/pypi/smstrade/
.. _Git Repository: https://gitorious.org/python-smstrade/python-smstrade
.. _pip: https://pypi.python.org/pypi/pip/
.. _virtualenv: https://pypi.python.org/pypi/virtualenv/

Usage
-----

Sending SMS
...........

You may either use the API for SMS sending::

    import smstrade

    api = smstrade.SMSTrade()
    api.key = 'yourkey'
    api.send_sms(['00491701234567'], 'Test message')

or do the same with the command line tool::

    smstrade_send --key yourkey 00491701234567 'Test message'

You get help for the command line tool by running::

    smstrade_send -h

.. note::

    You can place all the configuration values into an ini file. See
    examples/smstrade.ini for an example. Before you really send SMS messages
    you need to put ``debug = False`` in your smstrade.ini.

    The file smstrade.ini is searched in system dependent paths as well as in
    the current directory. The search path is printed when invoking
    :literal:`smstrade_send -h` together with the description of the
    ``--config`` parameter.

    The smstrade.ini file is shared with the smstrade_balance tool.

Getting the account balance
...........................

Use the API for getting your account balance::

    import smstrade

    api = smstrade.SMSTradeBalanceAPI()
    api.key = 'yourkey'
    balance = api.get_balance()

or do the same with the command line tool::

    smstrade_balance --key yourkey
