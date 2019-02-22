import logging
import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_jwt_extended import get_jwt_identity, jwt_optional
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

from qwc_services_core.jwt import jwt_manager
from registration_gui import RegistrationGUI


# Flask application
app = Flask(__name__)
app.secret_key = os.environ.get('JWT_SECRET_KEY', os.urandom(24))

# enable CSRF protection
CSRFProtect(app)
# load Bootstrap extension
Bootstrap(app)

# Setup the Flask-JWT-Extended extension
jwt = jwt_manager(app)


# Setup mailer
def mail_config_from_env(app):
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', '127.0.0.1')
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 25))
    app.config['MAIL_USE_TLS'] = os.environ.get(
        'MAIL_USE_TLS', 'False') == 'True'
    app.config['MAIL_USE_SSL'] = os.environ.get(
        'MAIL_USE_SSL', 'False') == 'True'
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
    app.config['MAIL_DEBUG'] = int(os.environ.get('MAIL_DEBUG', app.debug))
    app.config['MAIL_MAX_EMAILS'] = os.environ.get('MAIL_MAX_EMAILS')
    app.config['MAIL_SUPPRESS_SEND'] = os.environ.get(
        'MAIL_SUPPRESS_SEND', str(app.testing)) == 'True'
    app.config['MAIL_ASCII_ATTACHMENTS'] = os.environ.get(
        'MAIL_ASCII_ATTACHMENTS', False)


mail_config_from_env(app)
mail = Mail(app)

# create Registration GUI
registration_gui = RegistrationGUI(mail, app.logger)


@app.route('/register', methods=['GET', 'POST'])
@jwt_optional
def register():
    return registration_gui.register(get_jwt_identity())


# local webserver
if __name__ == '__main__':
    print("Starting QWC Registration GUI...")
    app.logger.setLevel(logging.DEBUG)
    app.run(host='localhost', port=5032, debug=True)
