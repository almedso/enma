# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
import pytest
from flask import url_for

from enma.user.models import User
from tests.test_enma.factories import UserFactory
from enma.user.admin import establish_admin_defaults


class TestLoggingIn:
    """
    Login work flow is as follow

    .. actdiag::

        actdiag {
          begin -> portal -> login -> user -> end
          login -> resent -> user
          login -> error -> login
          error -> end
          resent -> confirm_email -> confirm -> end

          lane control {
              begin [shape = "beginpoint"];
              end [shape = "endpoint"];
          }

          lane public {
             label = "Public"
             portal [label = "Portal of WebApp"];
             login  [label = "Login"];
             error  [label = "Login error (not active or wrong credentials)"];
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

    Pretty easy is the logout workflow:

    A prerequisite is that a user is actually logged in.
    If not a not authorized page will be shown.

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



    Only local authentication is tested automatically.
    Authentication using OpenId is covered by manual tests.

    Note: it is possible to login, even if another user is already
    logged in. The old user will be overwritten (in the session context)
    by the new user. To do so it is required to enter the login url
    manually. I.e. while a user is logged in there is no link available
    that leads to the login page.
    """

    def test_can_log_in_returns_200(self, user, testapp):
        """
        Test that User can successfully login (using local authentication)
        """
        # Goes to login page
        res = testapp.get("/")
        # Clicks Login button
        res = res.click("Login")
        form = res.forms['login_userpassword']
        form['up-username'] = user.username[:-6]
        form['up-password'] = 'myprecious'
        # Submits
        res = form.submit(name='up-login').follow()

    def test_sees_alert_on_log_out(self, user, testapp):
        """
        Test that a user who is logged in, can logout.
        """
        # Goes to login page
        res = testapp.get("/")
        # Clicks Login button
        res = res.click("Login")
        form = res.forms['login_userpassword']
        form['up-username'] = user.username[:-6]
        form['up-password'] = 'myprecious'
        # Submits
        res = form.submit(name='up-login').follow()
        res = testapp.get(url_for('public.logout')).follow()
        # sees alert
        assert 'You are logged out.' in res

    def test_sees_error_message_if_password_is_incorrect(self, user, testapp):
        """
        Test that a user fails to login if (s)he provides a wrong password
        """
        # Goes to login page
        res = testapp.get(url_for("public.login"))
        form = res.forms['login_userpassword']
        form['up-username'] = user.username[:-6]
        form['up-password'] = 'wrong'
        # Submits
        res = form.submit(name='up-login')
        # sees error
        assert res.status_int == 200
        # not possible to inject correct values for the up-login submit button
        assert "Invalid password" in res

    def test_sees_error_message_if_username_doesnt_exist(self, user, testapp):
        """
        Test that a user cannot log in if (s)he provide a wrong username
        """
        # Goes to login page
        res = testapp.get(url_for("public.login"))
        form = res.forms['login_userpassword']
        form['up-username'] = 'unknown'
        form['up-password'] = 'myprecious'
        # Submits
        res = form.submit(name='up-login')
        # sees error
        assert res.status_int == 200
        assert "Unknown user" in res


class TestRegistering:
    """
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

    """

    def test_can_register(self, user, testapp):
        old_count = len(User.query.all())
        # Goes to homepage
        res = testapp.get("/")
        # Clicks Create Account button
        res = res.click("Create account")
        # Fills out the form
        form = res.forms["register_userpassword"]
        form['up-username'] = 'foobar'
        form['up-password'] = 'secret'
        form['up-confirm'] = 'secret'
        # Submits
        res = form.submit(name='up-register')
        print "Response: ", str(res)
        import sys
        sys.stdout.flush()
        res.follow()
        # A new user was created
        assert len(User.query.all()) == old_count + 1

    def test_sees_error_message_if_passwords_dont_match(self, user, testapp):
        # Goes to registration page
        res = testapp.get(url_for("public.register"))
        # Fills out form, but passwords don't match
        form = res.forms["register_userpassword"]
        form['up-username'] = 'foobar'
        form['up-password'] = 'secret'
        form['up-confirm'] = 'secrets'
        # Submits
        res = form.submit(name='up-register')
        # sees error message
        assert "Passwords must match" in res

    def test_sees_error_message_if_user_already_registered(self, user, testapp):
        user = UserFactory(active=True)  # A registered user
        user.save()
        # Goes to registration page
        res = testapp.get(url_for("public.register"))
        # Fills out form, but username is already registered
        form = res.forms["register_userpassword"]
        form['up-username'] = user.username[:-6]
        form['up-password'] = 'secret'
        form['up-confirm'] = 'secret'
        # Submits
        res = form.submit(name='up-register')
        # sees error
        assert "Username already registered" in res


@pytest.mark.usefixtures('db')
class TestEstablishAdminDefaults:

    def test_create_if_not_exists(self, db):
        admin = User.query.filter(User.username=='admin%local').first()
        if admin:
            db.session.delete(admin)
            db.session.commit()
        # no admin user exists anymore

        establish_admin_defaults()
        admin = User.query.filter(User.username=='admin%local').first()
        assert admin # admin user exists
        assert admin.check_password('admin') # has the password admin

    def test_site_admin_reset_passwd_if_exists(self, db):
        admin = User.query.filter(User.username=='admin%local').first()
        if admin:
            admin.set_password('not-admin')
        else:
            admin = User('admin%local', 'foo@test.com', password='not-admin')
        db.session.add(admin)
        db.session.commit()

        establish_admin_defaults()
        admin = User.query.filter(User.username=='admin%local').first()
        assert admin # admin user exists
        assert admin.check_password('admin') # has the password admin

    def test_set_site_admin_role(self, db):
        admin = User.query.filter(User.username=='admin%local').first()
        if not admin:
            admin = User('admin%local', 'foo@test.com')
            db.session.add(admin)
            db.session.commit()

        establish_admin_defaults()
        retrieved = User.query.filter(User.username=='admin%local').first()
        assert retrieved 
        assert retrieved.role.name == 'SiteAdmin'


class TestGetForgottenPassword:
    """
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

    This workflow only makes sense if the user is locally registered
    and has actually forgotten his password but remembers the username.
    """
    def test_reset_passwd(self, db):
        """
        Test if the user can reset his/her password.
        """
        #@todo
        pass


