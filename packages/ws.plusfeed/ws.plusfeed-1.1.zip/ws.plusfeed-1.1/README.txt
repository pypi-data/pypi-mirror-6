========
plusfeed
========

plusfeed reads the activities of a `Google Plus`_ user and converts them into
an Atom feed.

* Get a Google Plus `API key`_. This enables read-only access and does not sign
  you into Google Plus.
* Install from PyPI with ``pip install ws.plusfeed``
* Run ``plusfeed USER-ID YOUR-API-KEY`` to create an atom feed.
  (The USER-ID can be found by clicking around on Google Plus until you find
  an URL that looks like ``https://plus.google.com/117962666888533781522``).

Example to get the `CyanogenMod`_ feed if you put your API key into
``~/.pluskey``::

    $ plusfeed 117962666888533781522 `<~/.pluskey` > cyanogenmod.atom


.. _`Google Plus`: https://plus.google.com/
.. _`API key`: https://developers.google.com/+/api/oauth#apikey
.. _`CyanogenMod`: http://cyanogenmod.org/
