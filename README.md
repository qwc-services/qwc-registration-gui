Registration GUI for QWC Services
=================================

Provides an application form, so users can submit group membership requests.

These membership requests can then be approved or declined by an admin user in the [QWC configuration backend](https://github.com/qwc-services/qwc-admin-gui).


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


Usage
-----

Run standalone application:

    python server.py

Registration form (if user is signed in):

    http://localhost:5032/register


Development
-----------

Install Python module for PostgreSQL:

    apt-get install python3-psycopg2

Create a virtual environment:

    virtualenv --python=/usr/bin/python3 .venv

Activate virtual environment:

    source .venv/bin/activate

Install requirements:

    pip install -r requirements.txt

Start local service:

    python server.py
