import logging
import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_jwt_extended import get_jwt_identity, jwt_optional
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

# create Registration GUI
registration_gui = RegistrationGUI(app.logger)


@app.route('/register', methods=['GET', 'POST'])
@jwt_optional
def register():
    return registration_gui.register(get_jwt_identity())


# local webserver
if __name__ == '__main__':
    print("Starting QWC Registration GUI...")
    app.logger.setLevel(logging.DEBUG)
    app.run(host='localhost', port=5032, debug=True)
