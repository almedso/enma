===========================
Authentication Requirements
===========================

Authentication Requirements
===========================

Authentication Methods
----------------------
At registration the (future) user has the choice to either:

* use **Local Authentication**, by maintaining a **username**/password
  combination
* use **OpenId Authentication**, whereby this site trusts that the openid
  provider does a proper authentication. Advantage for the user: He/She does
  not have to remember the account data of yet another account.

Later on the user has to stick to this kind of authentication method.

Enforce verified email Addressess
---------------------------------

User have to provide an email address, where information can be sent to.
In order to do so, It must be assured, that the user actually can access
this email account and read emails.

Workflows
=========

Self-registration Workflow
--------------------------

 The registration workflow is as follow

.. actdiag::

    actdiag {
       portal -> register -> profile -> send -> confirm -> end
       register -> activate -> end

       lane webapp {
          label = "Public"
          portal [label = "Portal of WebApp"];
          register  [label = "Register"];
       }
       lane user {
          label = "User"
          profile [label = "Edit profile data"];
          confirm [label = "Confirm email address"];
          end [label = "User is registered"];
       }
       lane email {
          label = "Email-System"
          send [label = "confirmation email"];
       }
       lane administrator {
          label = "Administrator"
          activate [label = "Activate account"];
       }
    }

At the *Register* page, the (future) user makes the decision to either use
**Local Authentication** or **OpenId Authentication**.

Login Workflow
--------------

Login work flow is as follow

.. actdiag::

     actdiag {
       begin -> portal -> login -> user -> end
       login -> resent -> user
       login -> error -> end
       resent -> confirm_email -> confirm -> end

       lane control {
           begin [shape = "beginpoint"];
           end [shape = "endpoint"];
       }

       lane public {
          label = "Public"
          portal [label = "Portal of WebApp"];
          login  [label = "Login"];
          error  [label = "Login failed (user not active)"];
       }
       lane user {
          label = "User"
          user [label = "Home of user and other pages"];
       }
       lane unconfirmed {
          label = "email unconfirmed"
          resent [label = "[Optional] email not confirmed"];
          confirm [label = "Confirm email address"];
       }
       lane email {
          label = "Email system"
          confirm_email [label = "Request email address confirmation",
                         shape = "mail"];
       }
     }


.. NOTE:: It is possible to login, even if another user is already
    logged in. The old user will be overwritten (in the session context)
    by the new user. To do so it is required to enter the login url
    manually. I.e. while a user is logged in there is no link available
    that leads to the login page.

Logout Workflow
---------------

A prerequisite is that a user is actually logged in.
If not a not authorized page will be shown.

Logout work flow is as follow:

.. actdiag::

    actdiag {
       beginpoint -> user -> logout -> portal -> endpoint
   
       lane control {
           beginpoint [shape = "beginpoint"];
           endpoint [shape = "endpoint"];
       }
   
       lane public {
          label = "Public"
          portal [label = "Portal of WebApp"];
       }
       lane user {
          label = "User"
          user [label = "Home of user and other pages"];
          logout [label = "Logout"];
       }
    }


Forgotten Password Workflow
---------------------------

* The workflow only applies if the user is locally registered.
* The user must remembers the username.

Forgotten password work flow is as follow

 .. actdiag::

     actdiag {
       begin -> portal -> login -> reset -> end
       reset -> pwd_email -> setpwd -> end

       lane control {
           begin [shape = "beginpoint"];
           end [shape = "endpoint"];
       }

       lane public {
          label = "Public"
          portal [label = "Portal of WebApp"];
          login  [label = "Login"];
          reset  [label = "Forgotten password"];
       }
       lane user {
          label = "User"
          setpwd [label = "Set new password"];
       }
       lane email {
          label = "Email system"
          pwd_email [label = "Password change access token",
                         shape = "mail"];
       }
     }

.. NOTE:: If the user does not remember his/her username, he/she needs to
   contact the administrator. (Resetting the password only if the email is
   known, does not make sense, since login in later on will fail.)

