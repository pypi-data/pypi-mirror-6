Shooju
=======

*shooju* is the official python client for `Shooju <http://www.shooju.com/>`_ with the following features:

- Authentication via username and api key
- Getting series points and fields
- Registering import jobs and writing and removing points and fields


Installation
-------------

Install using pip::

    pip install shooju

Basic Usage
------------

::

    >>> from shooju import Connection, sid, Point
    >>> from datetime import date
    >>> conn = Connection(server = <API_SERVER>, user = <USERNAME>, api_key = <API_KEY>)
    >>> job = conn.register_job('China Pop.')
    >>> series_id = sid("users", <USERNAME>, "china", "population")
    >>> job.put_point(series_id, Point(date(2012, 1, 1), 314.3))
    >>> job.put_field(series_id, "unit", "millions")
    >>> print conn.get_point(series_id, date(2012, 1, 1)).value
    313.3
    >>> print conn.get_field(series_id, "unit")
    millions

Source
-------

https://bitbucket.org/shooju/python-client

Changelist
-----------

0.3
^^^^

- Connection().scroll() fixed
- Initializing Connection doesn't ping the API
- If series does not exist get_point, get_points, get_field, get_fields return None

0.2
^^^^

- Connection().multi_get() renamed to mget()
- mget().get_points(), get_fields(), get_point() and get_field() return index of their result
- Connection().register_job() requires a description of more than 3 chars
- Connection().scroll_series() renamed to scroll()
- Renamed and rearranged Connection parameters: Connection(server, user, api_key)
- Field object removed, fields return a simple dict
- Points can have value of None