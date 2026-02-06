[![](https://github.com/qwc-services/qwc-registration-gui/workflows/build/badge.svg)](https://github.com/qwc-services/qwc-registration-gui/actions)
[![docker](https://img.shields.io/docker/v/sourcepole/qwc-registration-gui?label=Docker%20image&sort=semver)](https://hub.docker.com/r/sourcepole/qwc-registration-gui)

Registration GUI for QWC Services
=================================

Provides an application form, so users can submit group membership requests.

These membership requests can then be approved or declined by an admin user in the [QWC configuration backend](https://github.com/qwc-services/qwc-admin-gui) (if `GROUP_REGISTRATION_ENABLED` is set to `true` in the `qwc-admin-gui` configuration).


Setup
-----

Uses PostgreSQL connection service `qwc_configdb` (ConfigDB).

Setup PostgreSQL connection service file `pg_service.conf`:

```
[qwc_configdb]
host=localhost
port=5439
dbname=qwc_demo
user=qwc_admin
password=qwc_admin
sslmode=disable
```

Place this file in your home directory, or set the `PGSERVICEFILE` environment variable to point to the file.


Configuration
-------------

The following environment variables are supported:

| Name                         | Default       | Description                                                                               |
|------------------------------|---------------|-------------------------------------------------------------------------------------------|
| `ADMIN_RECIPIENTS`           | `None`        | Comma separated list of admin users who should be notified of new registration requests.  |
| `DEFAULT_LOCALE`             | `en`          | Admin GUI language (see [src/translations](src/translations) for available languages).    |
| `MAIL_SERVER`                | `localhost`   | Mailer setup, see [Flask-Mail](https://flask-mail.readthedocs.io/en/latest/#configuring). |
| `MAIL_PORT`                  | `25`          | Mailer setup, see [Flask-Mail](https://flask-mail.readthedocs.io/en/latest/#configuring). |
| `MAIL_USE_TLS`               | `False`       | Mailer setup, see [Flask-Mail](https://flask-mail.readthedocs.io/en/latest/#configuring). |
| `MAIL_USE_SSL`               | `False`       | Mailer setup, see [Flask-Mail](https://flask-mail.readthedocs.io/en/latest/#configuring). |
| `MAIL_DEBUG`                 | `app.debug`   | Mailer setup, see [Flask-Mail](https://flask-mail.readthedocs.io/en/latest/#configuring). |
| `MAIL_USERNAME`              | `None`        | Mailer setup, see [Flask-Mail](https://flask-mail.readthedocs.io/en/latest/#configuring). |
| `MAIL_PASSWORD`              | `None`        | Mailer setup, see [Flask-Mail](https://flask-mail.readthedocs.io/en/latest/#configuring). |
| `MAIL_DEFAULT_SENDER`        | `None`        | Mailer setup, see [Flask-Mail](https://flask-mail.readthedocs.io/en/latest/#configuring). |
| `MAIL_MAX_EMAILS`            | `None`        | Mailer setup, see [Flask-Mail](https://flask-mail.readthedocs.io/en/latest/#configuring). |
| `MAIL_SUPPRESS_SEND`         | `app.testing` | Mailer setup, see [Flask-Mail](https://flask-mail.readthedocs.io/en/latest/#configuring). |
| `MAIL_ASCII_ATTACHMENTS`     | `False`       | Mailer setup, see [Flask-Mail](https://flask-mail.readthedocs.io/en/latest/#configuring). |


### Translations

Translation strings are stored in a JSON file for each locale in `translations/<locale>.json` (e.g. `en.json`). Add any new languages as new JSON files.

Set the `DEFAULT_LOCALE` environment variable to choose the locale for the application form and notifications (default: `en`).


Run locally
-----------

Install dependencies and run:

    uv run src/server.py

Set `FLASK_DEBUG=1` for additional debug output.

Set `FLASK_RUN_PORT=<port>` to change the default port (default: `5000`).

Docker usage
------------

The Docker image is published on [Dockerhub](https://hub.docker.com/r/sourcepole/qwc-registration-gui).

See sample [docker-compose.yml](https://github.com/qwc-services/qwc-docker/blob/master/docker-compose-example.yml) of [qwc-docker](https://github.com/qwc-services/qwc-docker).
