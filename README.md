pressureNETAnalysis
===================

Web-based data viewer for pressureNET

## Local Development Setup

1.  Set up virtualenv (using virtualenvwrapper):

        mkvirtualenv pressurenet

1.  Activate virtualenv

        workon pressurenet

1.  Install all the local packages using pip:

        pip install -r requirements

1.  Copy `settings_local.py.ex` to `settings_local.py` and fill in the database settings (database name, username, password).

1.  Create the database and run through the database migrations:

        ./manage.py syncdb && ./manage.py migrate

1.  Run the server:

        ./manage.py runserver 0:8000

Check out how it looks in your browser: http://localhost:8000/ and http://localhost:8000/admin/

### Local Development Setup Using PostgreSQL

Replace the MySQL-Python package in requirements.txt with psycopg2. Make sure the postgresql-server-X.Y-dev package is installed.

Change the database backend from `django.db.backends.mysql` to `django.db.backends.postgresql_psycopg2`.
