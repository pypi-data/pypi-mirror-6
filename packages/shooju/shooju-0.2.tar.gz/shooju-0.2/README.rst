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