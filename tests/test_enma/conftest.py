# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
import os

import pytest
from webtest import TestApp

from enma.settings import TestConfig
from enma.app import create_app
from enma.database import db as _db
from tests.test_enma.factories import UserFactory
from enma.user.models import Role
from copy import deepcopy


@pytest.yield_fixture(scope='function')
def app():
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()
    yield _app
    ctx.pop()


@pytest.fixture(scope='session')
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.yield_fixture(scope='function')
def db(app):
    _db.app = app
    with app.app_context():
        _db.create_all()
        Role.insert_roles()
    yield _db
    _db.drop_all()


@pytest.fixture
def user(db):
    user = UserFactory(password='myprecious')
    db.session.commit()
    return user


@pytest.fixture
def logged_in(user, testapp):
    """
    Apply this fixture if you need to be logged in
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
    return res


#---!!! - almost fixture duplication - be careful - for access testing --!!!--

@pytest.yield_fixture(scope='function')
def app2():
    TestConfig2 = deepcopy(TestConfig)
    TestConfig2.TESTING = False  # do not test emailing but login_required
    _app = create_app(TestConfig2)
    ctx = _app.test_request_context()
    ctx.push()
    yield _app
    ctx.pop()


@pytest.fixture(scope='session')
def testapp2(app2):
    """A Webtest app."""
    return TestApp(app2)


@pytest.yield_fixture(scope='function')
def db2(app2):
    _db.app = app2
    with app2.app_context():
        _db.create_all()
        Role.insert_roles()
    yield _db
    _db.drop_all()


@pytest.fixture
def user2(db2):
    user = UserFactory(password='myprecious')
    db2.session.commit()
    return user