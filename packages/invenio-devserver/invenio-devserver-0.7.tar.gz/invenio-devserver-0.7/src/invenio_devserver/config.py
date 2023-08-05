"""
Default Values

INSTALL_PATH will be set to current active virtualenv or CFG_INVENIO_PREFIX if set.
SRC_PATH will be set to CFG_INVENIO_SRC if set otherwise ~/src/invenio/

All config values can be overwritten by puttinh a config_local.py in your
site-packages.
"""
import os

# Check if CFG_INVENIO_SRC is set otherwise use default.
if 'CFG_INVENIO_SRCDIR' in os.environ:
    SRC_PATH = [os.environ['CFG_INVENIO_SRCDIR']]
elif 'CFG_INVENIO_SRC' in os.environ:
    SRC_PATH = [os.environ['CFG_INVENIO_SRC']]
else:
    SRC_PATH = [os.path.expanduser("~/src/invenio"), ]


# Try if we're in a virtualenv or CFG_INVENIO_PREFIX is set.
INSTALL_PATH = "/opt/invenio/"
for var in ['VIRTUAL_ENV', 'CFG_INVENIO_PREFIX']:
    if var in os.environ:
        INSTALL_PATH = os.environ[var]
        break

# All the extensions specified here will be copied to their destination
# directories when they are changed
DIRS = {
    'py': 'lib/python/invenio',
    'js': 'var/www/js',
    'css': 'var/www/css',
    'conf': 'etc',
    'bft': 'etc/bibformat/format_templates',
    'bfo': 'etc/bibformat/output_formats',
}

STATIC_FILES = {
    '/img': '/var/www/img',
    '/js': '/var/www/js',
    '/flash': '/var/www/flash',
    '/css': '/var/www/css',
    '/static': '/var/www/static',
    '/export': '/var/www/export',
    '/MathJax': '/var/www/MathJax',
    '/jsCalendar': '/var/www/jsCalendar',
    '/ckeditor': '/var/www/ckeditor',
    '/mediaelement': '/var/www/mediaelement',
    '/ckeditor': '/var/www/ckeditor',
    '/robots.txt': '/var/www/robots.txt',
    '/favicon.ico': '/var/www/favicon.ico',
}

CONFIG_FILENAME = 'invenio.conf'
LOCAL_CONFIG_FILENAME = 'invenio-local.conf'

# Print a warning after xx seconds when processing a request
REQUEST_TIMEOUT = 0

# Spawns a server that will accept connections to be able to
# run arbitrary python code on the work
USE_CONSOLE = False


try:
    import config_local
    for setting in dir(config_local):
        if setting == setting.upper():
            globals()[setting] = getattr(config_local, setting)
except ImportError:
    pass
