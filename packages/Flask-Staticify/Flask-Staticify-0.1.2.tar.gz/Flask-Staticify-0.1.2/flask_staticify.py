# coding: utf-8

import os
from warnings import warn

from flask import current_app
from flask.helpers import safe_join, send_file
from werkzeug.exceptions import NotFound


def _fallback_to(folders):
    def send_static(filename):
        """Sends a file from the static folder if a given file exist.
        Otherwise, tries additional folders as a fallback.
        """
        try:
            return current_app.send_static_file(filename)
        except NotFound:
            for folder in folders:
                filepath = safe_join(folder, filename)
                if os.path.isfile(filepath):
                    current_app.logger.debug("Found, sending '%s' from '%s'",
                                             filename, folder)
                    return send_file(filepath)
            raise NotFound()
    return send_static

def mount_folders(app, folders):
    """Sets up the additional static locations that the application will traverse.
    This function does nothing in debug mode.
    """
    if app.debug:
        if app.view_functions['static'] != app.send_static_file:
            warn("The endpoint function was already redefined in your "
                 "application. Old changes will not show up.")
        app.view_functions['static'] = _fallback_to(set(folders))
