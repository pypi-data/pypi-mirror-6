Django Header Auth
==================

An extremely simple Django middleware for authorizing requests based on headers.

Installation
------------

1. Install via pip:

        :::bash
        $ pip install django-header-auth

2. Add the `HeaderAuthMiddleware`:

        :::python
        MIDDLEWARE_CLASSES = (
            # ...
            'header_auth.middleware.HeaderAuthMiddleware',
            # ...
        )

Usage
-----

Add a `HEADER_AUTH` dict containing the headers you'd like to check to the settings file:

    :::python
    HEADER_AUTH = {
        'HTTP_X_SOME_HEADER': 'sometoken',
        'HTTP_X_ANOTHER_HEADER': 'anothertoken',
    }

The request's headers will be checked for 'X-Some-Header: sometoken' and 'X-Another-Header: anothertoken' and simply pass through if everything is ok. Otherwise a 403 Forbidden will be returned.

Copyright
---------

Copyright (c) 2013 [LocalMed, Inc.](http://www.localmed.com/). See LICENSE for details.
