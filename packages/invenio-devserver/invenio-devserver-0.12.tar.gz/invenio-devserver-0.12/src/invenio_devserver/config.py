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

SPECIAL_DIRS = [
    # HTML Templates
    (ur"modules/(?P<module>[a-z]+)/etc/templates/.+\.html$", 'etc/%(module)s/templates/'),

    # Templates
    (ur"bibcatalog/ticket_templates/.+\.py$", 'lib/python/invenio/bibcatalog_ticket_templates'),
    (ur"websubmit/.+\.tpl$", 'etc/bibconvert/config'),

    # Bibformat elements/templates
    (ur"modules/bibformat/lib/elements/(bfe_)?test.+\.py$", 'var/tmp/tests_bibformat_elements'),
    (ur"modules/bibformat/lib/elements/.+\.py$", 'lib/python/invenio/bibformat_elements'),
    (ur"bibformat/format_elements/.+\.py$", 'lib/python/invenio/bibformat_elements'),
    (ur"modules/bibformat/etc/format_templates/Test.+\.bft$", 'var/tmp'),
    (ur"modules/bibformat/etc/output_formats/TEST*.+\.bfo$", 'var/tmp'),
    (ur"modules/webjournal/etc/.+\.bft$", 'etc/bibformat/format_templates/webjournal'),

    # Plugins
    (ur"modules/webjournal/lib/elements/.+\.py$", 'lib/python/invenio/bibformat_elements'),
    (ur"modules/bibcheck/lib/plugins/.+\.py$", 'lib/python/invenio/bibcheck_plugins'),
    (ur"modules/webstyle/lib/goto_plugins/.+\.py$", 'lib/python/invenio/goto_plugins'),
    (ur"modules/websubmit/lib/functions/.+\.py$", 'lib/python/invenio/websubmit_functions'),
    (ur"modules/miscutil/lib/upgrades/.+\.py$", 'lib/python/invenio/upgrades'),
    (ur"modules/bibindex/lib/tokenizers/.+\.py$", 'lib/python/invenio/bibindex_tokenizers'),
    (ur"modules/bibfield/lib/functions/.+\.py$", 'lib/python/invenio/bibfield_functions'),
    (ur"bibtasklets/bst_.+\.py$", 'lib/python/invenio/bibsched_tasklets'),
    (ur"modules/bibsched/lib/tasklets/.+\.py", 'lib/python/invenio/bibsched_tasklets'),
    (ur"bibharvest/bibfilter_.+\.py$", 'bin'),
    (ur"websubmit/.+\.py$", 'lib/python/invenio/websubmit_functions'),
    (ur"modules/websubmit/lib/.+_plugin\.py$", 'lib/python/invenio/websubmit_file_metadata_plugins'),
    (ur"modules/bibdocfile/lib/bom_textdoc\.py$", 'lib/python/invenio/bibdocfile_plugins'),
    (ur"modules/bibcatalog/lib/ticket_templates/.+\.py$", 'lib/python/invenio/bibcatalog_ticket_templates'),

    # Bibedit tests conf
    (ur"modules/bibedit/lib/bibedit_engine_unit_tests.conf$", 'var/www/js'),

    # Admin hooks
    (ur"modules/(?P<module>[a-z]+)/web/admin/.+\.py", 'var/www/admin/%(module)s'),
    (ur"modules/(?P<module>[a-z]+)/web/.+\.py", 'var/www'),
    (ur"webaccess/searchuser\.py$", 'var/www/admin'),

    # JS in sub directories
    (ur"modules/miscutil/etc/ckeditor_scientificchar/lang/.+\.js$", 'var/www/ckeditor/plugins/scientificchar/lang'),
    (ur"modules/miscutil/etc/ckeditor_scientificchar/dialogs/scientificchar\.js$", 'var/www/ckeditor/plugins/scientificchar/dialogs'),
    (ur"modules/miscutil/etc/ckeditor_scientificchar/.+\.js$", 'var/www/ckeditor/plugins/scientificchar'),
    (ur"modules/miscutil/etc/ckeditor_scientificchar/lang/.+\.js$", 'var/www/ckeditor/plugins/scientificchar/lang'),
    (ur"modules/bibencode/lib/.+\.js", 'lib/python/invenio'),
    (ur"modules/webstyle/etc/journal-editor-.+\.js$", 'var/www/ckeditor'),
    (ur"modules/oaiharvest/web/admin/.+\.js$", 'var/www/js'),
    (ur"modules/(?P<module>[a-z]+)/web/admin/.+\.js", 'var/www/static/%(module)s-admin-interface'),

    # Misplaced CSS
    (ur"modules/webauthorlist/web/.+\.css$", 'var/www/img'),
    (ur"modules/bibauthorid/web/.+\.css$", 'var/www/img'),
    (ur"modules/webstyle/css/.+\.css$", 'var/www/img'),
    (ur"modules/webjournal/css/.+\.css$", 'var/www/img'),
    (ur"modules/webjournal/etc/.+\.css$", 'var/www/img'),
    (ur"modules/oaiharvest/web/admin/.+\.css$", 'var/www/img'),
    (ur"modules/bibedit/lib/.+\.css$", 'var/www/img'),
    (ur"modules/websearch/lib/.+\.css$", 'var/www/img'),
    (ur"modules/bibencode/www/.+\.css$", 'var/www/img'),
    (ur"modules/webstyle/etc/.+\.js", 'var/www/ckeditor'),
    (ur"modules/webjournal/lib/widgets/.+\.py$", 'lib/python/invenio/bibformat_elements'),
    (ur"modules/webstyle/etc/.+\.css$", 'var/www/ckeditor'),
    (ur"webstyle/.+\.css$", 'var/www/img'),
]

SPECIAL_DIRS_RE = [(re.compile(pattern , re.U|re.I), dest_dir) for pattern, dest_dir in SPECIAL_DIRS]

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

IGNORE_FILES = [
    ur"kbs/.+_dynamic_KB\.py$",
    ur"bibindex/create_index_tables\.py$",
    ur"kbs/kb_load\.py$",
    ur"webaccess/searchuser\.py$",
    ur"feedboxes/inspire_update_feedboxes\.py$",
    ur"bibindex/create_index_tables\.py$",
    ur"webstyle/invenio_inspire_ugly\.css$",
    ur"bibconvert/split_large_spires_dump_file\.py$",
    ur"kbs/kb_regression_tests\.py$",
    ur"po/i18n_extract_from_wml_source\.py$",
    ur"modules/miscutil/lib/intbitset_setup\.py$",
    ur"modules/miscutil/lib/kwalitee\.py$",
    ur"modules/miscutil/lib/testimport\.py$",
    ur"modules/websession/lib/webuser_unit_tests\.py$",
    ur"modules/miscutil/lib/inveniocfg_dumperloader\.py$",
    ur"modules/bibdocfile/lib/fulltext_files_migration_kit\.py$",
    ur"websearch/inspire_search_tests\.py$",
    ur"po/i18n_update_wml_target\.py$",
    ur"modules/miscutil/lib/pep8\.py$",
    ur"modules/websession/lib/password_migration_kit\.py$",
    ur"configure-tests\.py$",
    ur"modules/miscutil/lib/web_api_key_unit_tests\.py$",
    ur"modules/bibdocfile/lib/icon_migration_kit\.py$",
    ur"modules/webaccess/lib/collection_restrictions_migration_kit\.py$",
    ur"modules/webbasket/lib/webbasket_migration_kit\.py$",
    # Old files
    ur"modules/bibformat/etc/output_formats/UNTLD\.bfo$",
    ur"modules/bibauthorid/lib/backbone-min\.js$",
    ur"modules/bibauthorid/lib/bibauthorid_dbinterface_old\.py$",
    ur"modules/bibrank/lib/bibrank_publication_grapher\.py$",
]

IGNORE_FILES_RE = {re.compile(pattern , re.U|re.I) for pattern in IGNORE_FILES}


CONFIG_FILENAME = 'invenio.conf'
LOCAL_CONFIG_FILENAME = 'invenio-local.conf'
