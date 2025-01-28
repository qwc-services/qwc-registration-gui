import logging
import os

from flask import Flask, json, jsonify, redirect, request
from flask_bootstrap import Bootstrap5
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

from qwc_services_core.auth import auth_manager, optional_auth, get_identity
from qwc_services_core.tenant_handler import TenantHandler, \
    TenantPrefixMiddleware, TenantSessionInterface
from registration_gui import RegistrationGUI


AUTH_PATH = os.environ.get('AUTH_PATH', '/auth')
SKIP_LOGIN = os.environ.get('SKIP_LOGIN', False)

# Flask application
app = Flask(__name__)

jwt = auth_manager(app)
app.secret_key = os.environ.get('JWT_SECRET_KEY', os.urandom(24))

# JWT CSRF protection conflicts with WTF CSRF protection
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['WTF_CSRF_SSL_STRICT'] = os.environ.get(
    'WTF_CSRF_SSL_STRICT', 'True').lower() == 'true'

# create tenant handler
tenant_handler = TenantHandler(app.logger)

# enable CSRF protection
CSRFProtect(app)
# load Bootstrap extension
Bootstrap5(app)



# Setup mailer
def mail_config_from_env(app):
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', '127.0.0.1')
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 25))
    app.config['MAIL_USE_TLS'] = os.environ.get(
        'MAIL_USE_TLS', 'False').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get(
        'MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
    app.config['MAIL_DEBUG'] = int(os.environ.get('MAIL_DEBUG', app.debug))
    app.config['MAIL_MAX_EMAILS'] = os.environ.get('MAIL_MAX_EMAILS')
    app.config['MAIL_SUPPRESS_SEND'] = os.environ.get(
        'MAIL_SUPPRESS_SEND', str(app.testing)).lower() == 'true'
    app.config['MAIL_ASCII_ATTACHMENTS'] = os.environ.get(
        'MAIL_ASCII_ATTACHMENTS', False)


mail_config_from_env(app)
mail = Mail(app)

# Load translation strings
DEFAULT_LOCALE = os.environ.get('DEFAULT_LOCALE', 'en')
translations = {}
try:
    locale = DEFAULT_LOCALE
    path = os.path.join(app.root_path, 'translations/%s.json' % locale)
    with open(path, 'r') as f:
        translations[locale] = json.load(f)
except Exception as e:
    app.logger.error(
        "Failed to load translation strings for locale '%s' from %s\n%s"
        % (locale, path, e)
    )


# Setup translation helper
@app.template_filter('i18n')
def i18n(value, locale=DEFAULT_LOCALE):
    """Lookup string in translations.

    Usage:
        Python: i18n('example.path_to.string')
        Jinja2 filter for templates: 'example.path_to.string' | i18n

    :param str value: Dot-separated path to translation string
    :param str locale: Override locale (optional)
    """
    # traverse translations dict for locale
    parts = value.split('.')
    lookup = translations.get(locale, {})
    for part in parts:
        if isinstance(lookup, dict):
            # get next lookup level
            lookup = lookup.get(part)
        else:
            # lookup level too deep
            lookup = None
        if lookup is None:
            # return input value if not found
            lookup = value
            break

    return lookup


app.wsgi_app = TenantPrefixMiddleware(app.wsgi_app)
app.session_interface = TenantSessionInterface(os.environ)

def auth_path_prefix():
    # e.g. /admin/org1/auth
    return app.session_interface.tenant_path_prefix().rstrip("/") + "/" + AUTH_PATH.lstrip("/")


def registration_gui_handler():
    """Get or create a RegistrationGUI instance for a tenant."""
    tenant = tenant_handler.tenant()
    handler = tenant_handler.handler('registrationGui', 'registrationGui', tenant)
    if handler is None:
        handler = tenant_handler.register_handler(
            'registrationGui', tenant, RegistrationGUI(mail, i18n, app.logger))
    return handler

@app.before_request
@optional_auth
def assert_identity():
    identity = get_identity()
    if not identity:
        app.logger.info("Redirecting to login")
        prefix = auth_path_prefix()
        return redirect(prefix + '/login?url=%s' % request.url)

@app.route('/register', methods=['GET', 'POST'])
@optional_auth
def register():
    registration_gui = registration_gui_handler()

    return registration_gui.register(get_identity())


""" readyness probe endpoint """
@app.route("/ready", methods=['GET'])
def ready():
    return jsonify({"status": "OK"})


""" liveness probe endpoint """
@app.route("/healthz", methods=['GET'])
def healthz():
    return jsonify({"status": "OK"})


# local webserver
if __name__ == '__main__':
    print("Starting QWC Registration GUI...")
    app.logger.setLevel(logging.DEBUG)
    app.run(host='localhost', port=5032, debug=True)
