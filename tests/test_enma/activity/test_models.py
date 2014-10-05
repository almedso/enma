# -*- coding: utf-8 -*-
"""Model unit tests."""
from mock import patch

import pytest
from flask.ext.login import login_user

from enma.activity.models import Activity
import enma.activity.models
from enma.activity.models import record_api, record_authentication, \
    record_priviledge, record_user
from enma.activity.models import API, AUTHENTICATION, PRIVILEGE, USER


def test_create_and_get_repr(db):
    activity = Activity('actor', 'description')
    activity.save()
    retrieved = Activity.query.first()
    assert retrieved == activity
    assert 'actor' in str(retrieved)


def test_record(user):
    login_user(user)
    enma.activity.models.record('test-record', acted_on=user)
    retrieved = Activity.query.first()
    assert retrieved.actor == user.username
    assert retrieved.description == 'test-record'
    assert retrieved.acted_on == user.username


@patch('enma.activity.models.record')
def test_record_api(test_patch):
    record_api('description', 'acted_on')
    test_patch.assert_called_with('description', category=API,
                                  acted_on='acted_on')


@patch('enma.activity.models.record')
def test_record_api_without_acted_on(test_patch):
    record_api('description')
    test_patch.assert_called_with('description', category=API, 
                                  acted_on=None)


@patch('enma.activity.models.record')
def test_record_authentication(test_patch):
    record_authentication()
    test_patch.assert_called_with('Login',
                                  category=AUTHENTICATION)


@patch('enma.activity.models.record')
def test_record_authentication_with_logout(test_patch):
    record_authentication('Logout')
    test_patch.assert_called_with('Logout',
                                  category=AUTHENTICATION)


@patch('enma.activity.models.record')
def test_record_priviledge(test_patch):
    record_priviledge('acted_on')
    test_patch.assert_called_with('Change', acted_on='acted_on',
                                  category=PRIVILEGE)


@patch('enma.activity.models.record')
def test_record_priviledge_with_description(test_patch):
    record_priviledge('acted_on', 'Grant')
    test_patch.assert_called_with('Grant', acted_on='acted_on',
                                  category=PRIVILEGE)


@patch('enma.activity.models.record')
def test_record_user(test_patch):
    record_user('Register')
    test_patch.assert_called_with('Register', acted_on=None,
                                  category=USER)


@patch('enma.activity.models.record')
def test_record_user_with_user(test_patch):
    record_user('Register', 'acted_on')
    test_patch.assert_called_with('Register', acted_on='acted_on',
                                  category=USER)
