========
Usage
========

To use Entitlement Management WebApp in a project::

    import enma


User Authentication
===================

Various authentication methods are possible.
On the web site the user has the choise between

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

