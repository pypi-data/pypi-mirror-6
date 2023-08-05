=================
redisEventTracker
=================

EventTracker
------------
Class EventTracker is used to gather statistics for multiple events.
It uses a Redis set (store) as a backend.


Installation
------------

To install redis-event-tracker, simply:

.. code-block:: bash

    $ sudo pip install redis-event-tracker


API Reference
-------------

* **track_event()**: Method track_event() increases a counter for a given event name in the today's record.
If there were errors, they are logged into a log file.