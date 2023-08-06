wrap2: Library for wrapping social network wrappers
===================================================

The ``wrap2`` package is a wrapper for various social networks wrappers.
Various networks have different format for "posts". Twitter is chosen as standard, so other networks posts are
converted to be twitter-like.

.. image:: https://api.travis-ci.org/paylogic/wrap2.png
   :target: https://travis-ci.org/paylogic/wrap2
.. image:: https://pypip.in/v/wrap2/badge.png
   :target: https://crate.io/packages/wrap2/
.. image:: https://coveralls.io/repos/paylogic/wrap2/badge.png?branch=master
   :target: https://coveralls.io/r/paylogic/wrap2


Installation
------------

.. sourcecode::

    pip install wrap2

Usage
-----

.. code-block:: python

    from wrap2 import fbook
    fb = fbook.Facebook('id', 'secret')

    # get authorization url on Facebook
    url, opts = fb.get_authorization_url('http://example.com', scope=('read', 'write'))

    # get access token and profile info
    id, access_token, name, link = fb.on_authorization_callback(
        'http://facebook.com/some_callback_url', code='some code')

    # Put a post on the wall of the user authorized by ``access_token``.
    post = fb.post(access_token)


    from wrap2 import twitter
    tw = twitter.Twitter('id', 'secret')

    # get authorization url on Twitter
    url, opts = tw.get_authorization_url('http://example.com')

    # get access token and profile info
    id, (access_token_key, access_token_secret), name, link = tw.on_authorization_callback(
        'http://twitter.com/some_callback_url',
        oauth_verifier='some oauth verifier', request_token='some request token')

    # Put an update status of the user authorized by ``access_token``.
    post = tw.post(access_token)


Contact
-------

If you have questions, bug reports, suggestions, etc. please create an issue on
the `GitHub project page <http://github.com/paylogic/wrap2>`_.

License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

See `License <https://github.com/paylogic/wrap2/blob/master/LICENSE.txt>`_

© 2013 Paylogic International.
