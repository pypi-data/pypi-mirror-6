#!/usr/bin/env python

"""
Slingr- and Cob-specific wrapper around Eggsac.
Builds a Python package and all of its dependencies in a virtualenv,
wrapped up in a variety of formats.
"""

__all__ = (
    'eggsac',
    'eggsac_config',
)

import os

try:
    from eggsac.eggsac import eggsac
except ImportError:
    # Eggsac isn't installed. Look for it in the parallel Eggsac package
    import sys
    src_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."))

    sys.path.insert(0, os.path.join(src_root, "eggsac", "eggsac"))
    from eggsac import eggsac  # noqa


INI_FILENAME = 'cob.ini'
ALWAYS_UNZIP = ['pyyaml']
UWSGI_CONFIGURE = ("Slingr", "slingr/make_uwsgi_ini.py")
WSGI_FILE = ("Slingr", "slingr/wsgi_app.py")
LOCAL_PACKAGES = ['eggsac', 'slingr']
STATIC_FOLDER = 'output'


def eggsac_config(
        config_filename=None,
        always_unzip=None,
        uwsgi_configure=None,
        wsgi_file=None,
        local_packages=None,
        static_folder=None,
        **options
):
    src_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."))

    local_packages = LOCAL_PACKAGES + (local_packages or [])
    config = dict(
        config_filename=config_filename or INI_FILENAME,
        always_unzip=ALWAYS_UNZIP + (always_unzip or []),
        uwsgi_configure=uwsgi_configure or UWSGI_CONFIGURE,
        wsgi_file=wsgi_file or WSGI_FILE,
        local_packages=[os.path.join(src_root, p) for p in local_packages],
        static_folder=static_folder or STATIC_FOLDER,
    )
    config.update(options)
    return config
