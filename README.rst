======
README
======

**enma** is a abbreviation of Entitlement Management and comes along with
a user management, activity recording. It is open source.
Feel free to use and extend.

License
-------

MIT type.

Development
-----------

**enma** is a python app using **flask, jinja2, wtforms, bootrstrap,
sqlachemy, alembric ** and other.

The documentation is done the pythonic way using ReST format and shpinx tools.

The development approach is test driven. **pytest, webtest** and **mocks, 
patches**.

Deployment
----------

Production grade deployment will happen via *wsgi* container.

You need:
* A wsgi enabled web server
* A sql database that will hold your data 
* An email account where you can send emails from


Quickstart
----------

Install the source as follow and build the documentation.

.. code-block:: bash

   $ git clone https://github.com/volker_kempert/enma
   $ cd enma
   $ pip install -r requirements/dev.txt
   $ python setup.py sphinx_build

Read the installation chapter ad follow up the guidance


.. code-block:: bash

   $ firefox build/sphinx/html/index.html


