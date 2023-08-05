import traceback
import warnings
from functools import wraps


def replace_error_handler():
    from invenio import errorlib

    def error_handler(stream='error',
                      req=None,
                      prefix='',
                      suffix='',
                      alert_admin=False,
                      subject=''):
        print traceback.format_exc()[:-1]

    errorlib.register_exception = error_handler


def wrap_warn():

    @wraps(warnings.showwarning)
    def cb_showwarning(message=None, category=None, filename=None, lineno=None, file=None, line=None):
        print "WARNING: %(category)s: %(message)s (%(file)s:%(line)s)\n" % {
            'category': category,
            'message': message,
            'file': filename,
            'line': lineno}
        traceback.print_stack()

    warnings.showwarning = cb_showwarning


try:
    from invenio.webinterface_handler_flask import create_invenio_flask_app
except ImportError:
    from invenio.webinterface_handler_wsgi import application
else:
    application = create_invenio_flask_app()
