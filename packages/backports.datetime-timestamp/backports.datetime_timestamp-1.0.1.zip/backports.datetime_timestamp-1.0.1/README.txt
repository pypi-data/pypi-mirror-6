backports.datetime_timestamp
============================

Backport of the `datetime.timestamp()
<http://docs.python.org/3.3/library/datetime.html#datetime.datetime.timestamp>`_ method added in Python 3.3.

    from backports.datetime_timestamp import timestamp
    import datetime

    dt = datetime.datetime.utcnow()
    # instead of dt.timestamp(), use
    timestamp(dt)
