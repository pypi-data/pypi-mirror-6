IsCool Entertainment Bellman SDK (Pushd Python SDK)
===================================================
.. image:: https://badge.fury.io/py/iscool_e.bellman.png
    :target: http://badge.fury.io/py/iscool_e.bellman

This client library is designed to support the `Pushd API`_.

Pushd is an unified pushd server for server-side notification to mobile native apps, web apps etc. You can read more about Pushd on the link above.


Requirements
------------
This library relies on Requests_ since version 0.3.


Why Bellman ?
-------------
The alert sound when receiving a mobile notification is reminiscent to the officer of the court who made public announcements in the streets, back to the Middle Ages.


Usage
-----

Import the library and instanciate the API class::

    from iscool_e.bellman import pushd
    
    api = pushd.API()
    api.createSubscriber('apns', 'token')
    api.subscribe('id', 'event_name')
    api.sendMessage('event_name', 'Hello World!')


License
-------

This package is released under the MIT License.
Please see LICENSE document for a full description.

.. _`Pushd API`: http://github.com/rs/pushd
.. _Requests: http://github.com/kennethreitz/requests
