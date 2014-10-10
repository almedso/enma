========================
Software Design Concepts
========================

Model, View, Form Processing
============================

Flask typical approach is organize functional package as as a blueprint
an have the same patterns applied:

* Model most often by sqlalchemy model
* View function handle requests and return responses
* Form classes implement form handling


User Authentication
===================

Various authentication methods are possible.
On the web site the user has the choice between

* Local Authentication
* delegate toe authentication to an OpenId Provider

It is possible change the authentication method.

OpenID Authentication
---------------------

OpenID provider can be used for authentication.
It is checked for 

* nickname
* if nickname is not available email is tried.

The result is stored at username. 
Also the openid_provider must fit.

Local Authentication
--------------------

User who authenticate locally use a combination of username and
password. The openid_provider field must be set to local.

Password is stored hashed and salted (via bcrypt).


Access Control
==============

Ownership of Data and public Access
-----------------------------------

Any data belongs to a specific user. (e.g. Profile data like first name,
last name)

The owner always has complete access to his data. So this implicitly modeled.
It does not require checking of any access privileges. The access/ ownership
is assured by view function decorators (logged in user).

All user have access to information on public pages, Again, this is implicitly
modeled. It does not require checking of any access privileges. So no
view function decorator is required.

Access privileges
-----------------

To access or modify other users data, a user must have appropriate access
privileges.

This privileges are checked via view function decorators.