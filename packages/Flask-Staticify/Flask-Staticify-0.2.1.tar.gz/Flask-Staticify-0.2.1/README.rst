Flask-Staticify
===============

A simple extension that makes it possible to define the additional static locations
your Flask application will traverse as a fallback.

Only works when ``app.debug`` is set to ``True``.

Usage
-----

Let's have an example from the scratch:

.. code:: python

    >>> from flask.ext.staticify import mount_folders
    >>> app.debug = True

    # Ah, snap!
    >>> app.test_client().get('/static/app.js')
    <Response [404]>

    >>> STATICIFY_FOLDERS = (
    ...    os.path.join(app.root_path, 'tmp'),
    ...    ('prefix', 'path/to/folder')
    >>> )
    # Mounting will override the endpoint='static' view function
    # to look also into the additional folders as a fallback.
    >>> mount_folders(app, STATICIFY_FOLDERS)

    # And that's it!
    >>> app.test_client().get('/static/app.js')
    <Response [200]>

API
---

mount_folders(*app*, *locations*)
`````````````````````````````````
A single top-level function where the all magic comes from.

locations
  an iterable of strings with the additional static locations. It also accepts a 2-tuple of the form ``(prefix, folder)`` 
  and using a *prefix* is a way to connect specific urls with a *folder* directly.
  


Install
-------

::

    $ pip install Flask-Staticify
