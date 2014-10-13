# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
import pytest
from mock import Mock
from flask import url_for

from enma.user.models import User, Permission
from tests.test_enma.factories import UserFactory
from enma.user.admin import establish_admin_defaults
from webtest.app import AppError
from enma.extensions import mail


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
        """
        Test that a user can successfully register (via local authentication)
        """
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
        res.follow()
        # A new user was created
        assert len(User.query.all()) == old_count + 1

    def test_sees_error_message_if_passwords_dont_match(self, user, testapp):
        """
        Test that fails to locally register if he/she the gives none-matching
        passwords.
        """
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
        """
        Test that a user cannot register if the chosen (local) username is
        already used by another user.
        """
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
    """
    Tests that assure the the default SiteAdmit can be established again,
    even if due to some human error the password gots forgotten or some
    of the privileges were rewoked.
    """
    def test_create_if_not_exists(self, db):
        """
        Test that a SiteAdmin user can be created if he/she does not exist.
        """
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
        """
        Test that for an existing SiteAdmin the password gets reset to admin
        """
        admin = User.query.filter(User.username=='admin%local').first()
        if admin:
            admin.set_password('not-admin')
        else:
            admin = User('admin%local', 'foo@test.com', password='not-admin')
        db.session.add(admin)
        db.session.commit()
        admin.set_password('not-admin')

        establish_admin_defaults()
        admin = User.query.filter(User.username=='admin%local').first()
        assert admin # admin user exists
        assert admin.check_password('admin') # has the password admin

    def test_set_site_admin_role(self, db):
        """
        Test that for an existing SiteAdmin the role SiteAdmin gets assigned
        """
        admin = User.query.filter(User.username=='admin%local').first()
        if not admin:
            admin = User('admin%local', 'foo@test.com')
        admin.set_role('User')
        db.session.add(admin)
        db.session.commit()

        establish_admin_defaults()
        retrieved = User.query.filter(User.username=='admin%local').first()
        assert retrieved 
        assert retrieved.role.name == 'SiteAdmin'

    def test_set_site_admin_active(self, db):
        """
        Test that for an existing SiteAdmin the user is actually active
        """
        admin = User.query.filter(User.username=='admin%local').first()
        if not admin:
            admin = User('admin%local', 'foo@test.com')
        admin.active = False
        db.session.add(admin)
        db.session.commit()

        establish_admin_defaults()
        retrieved = User.query.filter(User.username=='admin%local').first()
        assert retrieved 
        assert retrieved.active

class TestUserPagesAndSettings:
    """
    Test the user pages and settings
    """

    def test_access_user_home_after_login(self, user, testapp):
        """
        Test that User can access his home page (dash board) after login
        """
        res = testapp.get(url_for('user.home'))
        print res
        res.mustcontain(no="401")

    def test_access_user_activity_after_login(self, logged_in, user, testapp):
        """
        Test that User can access his activity log after login
        """
        testapp.get(url_for('activity.home'))

    def test_access_user_profile_after_login(self, logged_in, user, testapp):
        """
        Test that User can access his profile after login
        """
        res = testapp.get(url_for('user.profile'))
        form = res.forms['editForm']
        form['firstname'] = 'First Name'
        form['lastname'] = 'Last Name'
        form['email'] = 'foo@bar.org'
        res = form.submit(name='apply').maybe_follow()
        assert 'First Name' == user.first_name
        assert 'Last Name' == user.last_name
        assert 'foo@bar.org' == user.email
        assert not user.email_validated

    def test_change_password_after_login_old_wrong(self, logged_in,
                                                     user, testapp):
        """
        Test that User can access change password page after login
        """
        res = testapp.get(url_for('user.password'))
        form = res.forms['chpwdForm']
        form['oldpassword'] = 'blabla'
        form['password'] = 'newpassword'
        form['confirm'] = 'newpassword'
        res = form.submit(name='setpwd').maybe_follow()
        assert 'Old password is wrong' in res
        assert user.check_password('myprecious')

    def test_access_user_change_password_after_login(self, logged_in,
                                                     user, testapp):
        """
        Test that User can access change password page after login
        """
        res = testapp.get(url_for('user.password'))
        form = res.forms['chpwdForm']
        form['oldpassword'] = 'myprecious'
        form['password'] = 'newpassword'
        form['confirm'] = 'newpassword'
        res = form.submit(name='setpwd').maybe_follow()
        assert user.check_password('newpassword')
        assert 'Your password has been updated' in res

    def test_access_user_token(self, logged_in, user, testapp):
        """
        Test that User can access the rest token page
        """
        res = testapp.get(url_for('user.token'))
        res.mustcontain(no="401")

    def test_access_user_terminate_page_success(self, logged_in, user, testapp):
        """
        Test that User can access account terminate page
        """
        username = user.username
        res = testapp.get(url_for('user.terminate'))
        form = res.forms['DeleteForm']
        form['delete_form-safety_question'] = 1
        res = form.submit(name='delete_form-delete').maybe_follow()
        assert None == User.query.filter_by(username=username).first()

    def test_access_user_terminate_page_fail(self, logged_in, user, testapp):
        """
        Test that User can access account terminate page
        """
        username = user.username
        res = testapp.get(url_for('user.terminate'))
        form = res.forms['DeleteForm']
        form['delete_form-safety_question'] = 0
        res = form.submit(name='delete_form-delete').maybe_follow()
        assert User.query.filter_by(username=username).first()
        assert 'Please confirm' in res

class TestForbiddenAccess():
    """
    Test if pages that require a login are not reachable if no user is
    logged in. 
    .. NOTE:: Requires !!!modified testfixtures!!! since the login_required
       decorator is normally switched of for testing
    """

    def test_forbitten_access_to_user_home(self, user2, testapp2):
        """
        Test that User cannot access his home page without login
        """
        with pytest.raises(AppError):  # we do expect a 401 status code
            testapp2.get(url_for('user.home'))

    def test_forbitten_access_to_user_activity(self, user2, testapp2):
        """
        Test that User cannot access his activity log without login
        """
        with pytest.raises(AppError):  # we do expect a 401 status code
            testapp2.get(url_for('activity.home'))

    def test_forbitten_access_to_user_profile(self, user2, testapp2):
        """
        Test that User cannot access his profile without login
        """
        with pytest.raises(AppError):  # we do expect a 401 status code
            testapp2.get(url_for('user.profile'))

    def test_forbitten_access_to_change_password(self, user2, testapp2):
        """
        Test that User cannot access change password page without login
        """
        with pytest.raises(AppError):  # we do expect a 401 status code
            testapp2.get(url_for('user.password'))

    def test_forbitten_access_to_token_page(self, user2, testapp2):
        """
        Test that User cannot access rest token page without login
        """
        with pytest.raises(AppError):  # we do expect a 401 status code
            testapp2.get(url_for('user.token'))

    def test_forbitten_access_to_terminate_account(self, user2, testapp2):
        """
        Test that User cannot access terminate account without login
        """
        with pytest.raises(AppError):  # we do expect a 401 status code
            testapp2.get(url_for('user.terminate'))


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
    def test_reset_passwd_email_sent(self, user, testapp):
        """
        Test if the user can reset his/her password.
        """
        res = testapp.get(url_for('public.forgotten_password'))
        # Fill in the form
        form = res.forms['forgotten_pwd']
        form['username'] = user.username[:-6]
        # Submits
        with mail.record_messages() as outbox:
            assert len(outbox) == 0
            res = form.submit(name='request').follow()
            assert len(outbox) == 1
            assert 'Set new password' in outbox[0].subject

    def test_reset_passwd_page_changes_password(self, user, testapp):
        """
        Test reset password side allows resetting the password
        """
        res = testapp.get(url_for('user.set_password',
                                  token=user.generate_auth_token(1)))
        # Fill in the form
        form = res.forms['set_password']
        form['password'] = 'newpassword'
        form['confirm'] = 'newpassword'
        res = form.submit(name='setpwd').follow()

        assert user.check_password('newpassword')


class TestValidateEmail:
    """
    Test the email address validation workflow  
    """
    @pytest.mark.usefixtures('logged_in')
    def test_send_email_changing_profile(self, user, testapp):
        """
        Test if the user will get an email after changing profile data
        """
        res = testapp.get(url_for('user.profile'))
        form = res.forms['editForm']
        form['firstname'] = 'First Name'
        form['lastname'] = 'Last Name'
        form['email'] = 'foo@bar.org'
        with mail.record_messages() as outbox:
            assert len(outbox) == 0
            res = form.submit(name='apply').maybe_follow()
            assert len(outbox) == 1
            assert 'Confirm your mail address' in outbox[0].subject

    def test_email_reminder(self, logged_in, user, testapp):
        """
        Test if a reminder comes up after login and test resent
        """
        res = logged_in
        assert 'confirmation' in res
        with mail.record_messages() as outbox:
            assert len(outbox) == 0
            res.click('Click here')
            assert len(outbox) == 1
            assert 'Confirm your mail address' in outbox[0].subject

    def test_email_link_validates(self, user, testapp):
        """
        Test if received link actually validates
        """
        user.email_validated = False
        user.save()
        testapp.get(url_for('user.confirm_email',
                            token=user.generate_auth_token(1)))

        assert user.email_validated


@pytest.mark.usefixtures('logged_in')
class TestUserManagementPages:
    """
    Test the user management pages
    """

    def test_user_access_to_user_list_not_permitted(self, user, testapp):
        """
        Test that User cannot access user members
        """
        with pytest.raises(AppError):
            testapp.get(url_for('user.members'))

    def test_user_manager_access_user_list(self, user, testapp):
        """
        Test that User cannot access user members
        """
        user.role.permissions = Permission.READ_USER
        user.save()
        res = testapp.get(url_for('user.members'))
        assert user.nickname in res

    def test_user_access_to_other_users_data_not_permitted(self, user, testapp):
        """
        Test that User cannot access other users data
        """
        with pytest.raises(AppError):
            testapp.get(url_for('user.edit', name=user.username))

    def test_user_manager_edits_user_data(self, user, testapp):
        """
        Test that User Manager edits other users data
        """
        user.role.permissions = Permission.UPDATE_USER
        user.save()
        res = testapp.get(url_for('user.edit', name=user.username))
        assert user.nickname in res

    def test_user_access_to_delete_other_not_permitted(self, user, testapp):
        """
        Test that User cannot access the page to delete other users data
        """
        with pytest.raises(AppError):
            testapp.get(url_for('user.delete', name=user.username))

    def test_user_manager_deletes_users_account(self, user, testapp):
        """
        Test that User Manager deletes a user account
        """
        user.role.permissions = Permission.DELETE_USER
        user.save()
        res = testapp.get(url_for('user.delete', name=user.username))
        assert user.nickname in res

    def test_user_access_to_adminstrate_not_permitted(self, user, testapp):
        """
        Test that User cannot access the page to delete other users data
        """
        with pytest.raises(AppError):
            testapp.get(url_for('user.admin', name=user.username))

    def test_user_manager_de_activates_a_user(self, user, testapp):
        """
        Test that User Manager activates or deactivates a user
        """
        user.role.permissions = Permission.UPDATE_USER
        user.save()
        res = testapp.get(url_for('user.admin', name=user.username))
        assert user.nickname in res

    def test_user_manager_changes_other_users_role(self, user, testapp):
        """
        Test that User Manager changes a users role
        """
        user.role.permissions = Permission.UPDATE_USER
        user.save()
        res = testapp.get(url_for('user.admin', name=user.username))
        assert user.nickname in res

