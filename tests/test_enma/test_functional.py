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

    def test_can_log_in_returns_200(self, user, testapp):
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

