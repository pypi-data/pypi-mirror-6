# coding: utf-8

import os
from warnings import warn

from flask import current_app
from flask.helpers import safe_join, send_file
from werkzeug.exceptions import NotFound


def _normalize(locations):
    rv = []
    for location in locations:
        if isinstance(location, (list, tuple)):
            prefix, folder = location
        else:
            prefix, folder = '', location
        rv.append((prefix, folder))
    return rv

def _fallback_to(locations):
    def send_static(filename):
        """Sends a file from the static folder if a given file exist.
        Otherwise, tries additional folders as a fallback.
        """
        try:
            return current_app.send_static_file(filename)
        except NotFound:
            for prefix, folder in locations:
                if prefix:
                    prefix = '{}{}'.format(prefix, os.sep)
                    if filename.startswith(prefix):
                        filename = filename[len(prefix):]
                filepath = safe_join(folder, filename)
                if os.path.isfile(filepath):
                    return send_file(filepath)
            raise NotFound()
    return send_static

def mount_folders(app, locations):
    """Sets up the additional static locations that the application will traverse.
    This function does nothing in debug mode.
    """
    if app.debug:
        if app.view_functions['static'] != app.send_static_file:
            warn("The endpoint function was already redefined in your "
                 "application. Old changes will not show up.")
        locations = _normalize(locations)
        app.view_functions['static'] = _fallback_to(locations)
