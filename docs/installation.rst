===========================
Installation and Deployment
===========================

General
=======

To install **enma** various concepts apply:

setup.py:
    To build a source tar ball and generate documentation
manage.py:
    Manage database, interact with main objects, run tests, run a dev server
wsgi.py:
     Encapsulation to run as wsgi app in any web server, i.e. it easily
     runs on a in to a PaaS provider like heroku or openshift.

Operation for development
=========================

To work in isolation it is recommended to run in a virtual environment.

Install virtual environment
---------------------------

Or, if you have virtualenv wrapper installed::

.. code-block:: bash

    $ virtualenv venv_enma
    $ source venv_enma/bin/activate

Install the source

.. code-block:: bash

    $ git clone https://github.com/volker_kempert/enma
    $ cd enma
    $ pip install -r requirements/dev.txt

Set the Environment
-------------------

You need to setup some essential environment variables to run the software.

You might add the following to ``.bashrc`` or ``.bash_profile`` or store
somewhere else.
If your mail server requires authentication to send emails, you have to provide
the password in plain text. Make sure, this email account is not a private
account but a structural account as well as make sure the location where you
store the password is sufficiently protected (no read rights for anybody but
you).

.. code-block:: bash

   # Core settings
   export ENMA_SECRET = 'something-really-secret'

   # Mail settings
   export MAIL_SERVER='your.smtp.server'
   export MAIL_PORT='587'
   export MAIL_USE_TLS=True
   # export MAIL_USE_SSL=True
   export MAIL_USERNAME='who.sends@the.mail'
   export MAIL_PASSWORD='secret'
   
Production environment
++++++++++++++++++++++

The production environment is tailored to run on the PaaS 
.. _Openshift: https://www.openshift.com
that additionally facilitates a postsql cartridge.

If you want to run **enma** from the local console in production mode
Additional environment variables have to be set:


.. code-block:: bash

   export ENMA_ENV = 'prod'  # for production only

   export OPENSHIFT_POSTGRESQL_DB_USERNAME='enma'
   export OPENSHIFT_POSTGRESQL_DB_PASSWORD='enma'
   export OPENSHIFT_POSTGRESQL_DB_HOST='localhost'
   export OPENSHIFT_POSTGRESQL_DB_PORT='5432'


Run Tests
=========

To run all tests, run ::

    python manage.py test

.. NOTE:: Test run in a separate test environment, no database config is
   required.


Create the Documentation
========================

To create the documentation, run ::

    python setup.py build_sphinx

.. NOTE:: It is essential to to this in the same environment as you run a
   development server, since sphinx imports all python modules.


Prepare the Database
====================

The ``ENMA_ENV`` environment variable which database gets prepared.
In your production environment (where the application is run via *wsgi*),
make sure the ``ENMA_ENV`` environment variable is set to ``"prod"``.

Then run the following commands to bootstrap your environment.

.. code-block:: bash

   $ python manage.py db init  # first time only
   $ python manage.py db migrate
   $ python manage.py db upgrade
   $ python manage.py establish_admin  # inject admin user and roles


Interactive Mode
----------------

Shell
+++++

To open the interactive shell, run ::

    python manage.py shell

By default, you will have access to ``app``, ``db``, and the ``User`` model.


Database Migrations
-------------------

Database migration apply to all development as well as production databases.

Whenever a database migration needs to be made. Run the following commands:

.. code-block:: bash

   $ python manage.py db migrate

This will generate a new migration script. Then run:

.. code-block:: bash

   $ python manage.py db upgrade

To apply the migration.

For a full migration command reference, run ``python manage.py db --help``.

Run the development server
--------------------------

Once source installed, environment variables set, database is prepared, you
can actually run the server from the command line:

.. code-block:: bash

   $ python manage.py server

and you can enter the web front:

.. code-block:: bash

   $ firefox http://localhost:5000


Running on OpenShift
====================
`Openshift <https://www.openshift.com/>`_
is a PaaS provider that allows to easily test and run python web applications.

**enma** is designed to provide a *wsgi* application that easily plugs in to
any web server, so it does on openshift.

Preparation
-----------

* Setup an account
* Setup an python 2.7 application
* Install the postgres cartridge

Installation
------------

* Follow openshifts git push mechanism, to install the software 
* Set the all environment variables as described in the 
  `Set Environment`_ section.
* Openshift takes care for: *OPENSHIFT_POSTGRESQL...* variables, no need to
  set them
* In order to prepare the database correctly, set *ENMA_ENV='prod'*, otherwise
  the database preparation will take the wrong database URI.
* Prepare the database as described at the
  `Prepare the Database`_ section.