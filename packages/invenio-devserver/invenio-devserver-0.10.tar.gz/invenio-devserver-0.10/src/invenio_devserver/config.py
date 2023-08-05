"""
Default Values

INSTALL_PATH will be set to current active virtualenv or CFG_INVENIO_PREFIX if set.
SRC_PATH will be set to CFG_INVENIO_SRC if set otherwise ~/src/invenio/

All config values can be overwritten by puttinh a config_local.py in your
site-packages.
"""
import os
import re

# Check if CFG_INVENIO_SRC is set otherwise use default.
if 'CFG_INVENIO_SRCDIR' in os.environ:
    SRC_PATH = [os.environ['CFG_INVENIO_SRCDIR']]
elif 'CFG_INVENIO_SRC' in os.environ:
    SRC_PATH = [os.environ['CFG_INVENIO_SRC']]
else:
    SRC_PATH = [os.path.expanduser("~/src/invenio"), ]

# Check if CFG_INVENIO_SRC is set otherwise use default.
if 'CFG_INSPIRE_SRCDIR' in os.environ:
    SRC_PATH += [os.environ['CFG_INSPIRE_SRCDIR']]
elif 'CFG_INSPIRE_SRC' in os.environ:
    SRC_PATH += [os.environ['CFG_INSPIRE_SRC']]
else:
    SRC_PATH += [os.path.expanduser("~/src/inspire"), ]

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
    'html': None,
}

SPECIAL_DIRS = {
    ur"^modules/(?P<module>[a-z]+)/etc/templates/.+\.html": 'etc/%(module)s/templates/',
    ur"^modules/bibformat/lib/elements/.+\.py": 'lib/python/invenio/bibformat_elements',
    ur"^bibformat/format_elements/.+\.py": 'lib/python/invenio/bibformat_elements',
    ur"^modules/webjournal/lib/elements/.+\.py": 'lib/python/invenio/bibformat_elements',
    ur"^modules/bibcheck/lib/plugins/.+\.py": 'lib/python/invenio/bibcheck_plugins',
    ur"^modules/webstyle/lib/goto_plugins/.+\.py": 'lib/python/invenio/goto_plugins',
    ur"^modules/websubmit/lib/functions/.+\.py": 'lib/python/invenio/websubmit_functions',
    ur"^modules/miscutil/lib/upgrades/.+\.py": 'lib/python/invenio/upgrades',
    ur"^modules/bibindex/lib/tokenizers/.+\.py": 'lib/python/invenio/bibindex_tokenizers',
    ur"^modules/bibfield/lib/functions/.+\.py": 'lib/python/invenio/bibfield_functions',
}

SPECIAL_DIRS_RE = {re.compile(pattern , re.U|re.I): dest_dir for pattern, dest_dir in SPECIAL_DIRS.iteritems()}

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
    '/robots.txt': '/var/www/robots.txt',
    '/favicon.ico': '/var/www/favicon.ico',
}

CONFIG_FILENAME = 'invenio.conf'
LOCAL_CONFIG_FILENAME = 'invenio-local.conf'
