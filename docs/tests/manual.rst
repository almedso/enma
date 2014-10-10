===================================
Test Specification for manual Tests
===================================

Authentication Tests
====================

Test if user can register via OpenId provider
---------------------------------------------

When:
   A new user wants to register with a username not registered yet, using
   OpenId authentication method.

   * The user enters the portal -> register page
   * The users chooses an OpenId provider (optionally clicks Go)

Then:
   The new user authenticates on the OpenId provider page

Then:
   Returns to the profile page where at least username is filled in


.. NOTE::
   Testcase is executed with OpenId provider:

   * Use google (fails because it is deprecated -> moved to OAuth2)
   * Use yahoo
   * Use flickr
   * Use facebook (fails for some reason)

Test if user can Login via OpenId provider
------------------------------------------

When:
   An activated user wants to login via OpenId authentication method.

   * The user enters the portal -> login page
   * The users chooses an OpenId provider (optionally clicks Go)

Then:
   The user authenticates on the OpenId provider page

Then:
   The user is directed to his/her home page and is authenticated (logged in)


.. NOTE::
   Testcase is executed with OpenId provider:

   * Use google (fails because it is deprecated -> moved to OAuth2)
   * Use yahoo
   * Use flickr
   * Use facebook (fails for some reason)

Test if system sends email
--------------------------

I.e. Tests if the smtp server and account is correctly configured.

When:
   * An activated user logs in and goes to *profile* page
   * Changes the his/her email address to another valid email address
   * Saves the changes
Then:
   He/she receives an email. (with a link to verify)
