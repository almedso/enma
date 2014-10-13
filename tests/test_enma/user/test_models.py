# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import pytest

from enma.user.models import User, Role, AnonymousUser
from tests.test_enma.factories import UserFactory
import time

@pytest.mark.usefixtures('db')
class TestUser:
    """ Unit tests concerning the user object"""

    def test_get_by_id(self):
        user = User('foo', 'foo@bar.com')
        user.save()

        retrieved = User.get_by_id(user.id)
        assert retrieved == user

    def test_created_at_defaults_to_datetime(self):
        user = User(username='foo', email='foo@bar.com')
        user.save()
        assert bool(user.created_at)
        assert isinstance(user.created_at, dt.datetime)

    def test_password_is_nullable(self):
        user = User(username='foo', email='foo@bar.com')
        user.save()
        assert user.password is None

    def test_factory(self, db):
        user = UserFactory(password="myprecious")
        db.session.commit()
        assert bool(user.username)
        assert bool(user.email)
        assert bool(user.created_at)
        assert user.active is True
        assert user.check_password('myprecious')

    def test_check_password(self):
        user = User.create(username="foo", email="foo@bar.com",
                    password="foobarbaz123")
        assert user.check_password('foobarbaz123') is True
        assert user.check_password("barfoobaz") is False

    def test_set_password(self):
        user = User.create(username="foo", email="foo@bar.com", password="foo")
        assert user.check_password("foo") is True
        user.set_password('foobarbaz123')
        assert user.check_password('foobarbaz123') is True

    def test_set_role(self):
        u = UserFactory()
        assert u.role.name == 'User'
        u.set_role('SiteAdmin')
        assert u.role.name == 'SiteAdmin'

    def test_auth_token_correct_user(self):
        u1 = User(username='u1', email='u1@mail.org')
        u1.save()
        t = u1.generate_auth_token(5)  # valid for five seconds
        u2 = User.verify_auth_token(t)
        assert u2 == u1

    def test_auth_token_user_deleted(self, db):
        u1 = User(username='u1', email='u1@mail.org')
        u1.save()
        t = u1.generate_auth_token(5)  # valid for five seconds
        db.session.delete(u1)
        db.session.commit()
        assert None ==  User.verify_auth_token(t) # expired

    def test_auth_token_expiry(self, db):
        u1 = User(username='u1', email='u1@mail.org')
        u1.save()
        t = u1.generate_auth_token(1)  # valid for five seconds
        time.sleep(2)  # takes quite long and is not really a unit test anymore
        assert None ==  User.verify_auth_token(t) # expired

    def test_full_name_property(self):
        user = UserFactory(first_name="Foo", last_name="Bar")
        assert user.full_name == "Foo Bar"

    def test_nickname_and_auth_provider_property(self, db):
        u = User(username='nick%prov', email='u1@mail.org')
        assert 'nick' == u.nickname
        assert 'prov' == u.auth_provider
        u.username = 'nick'
        assert 'nick' == u.nickname
        assert 'not-set' == u.auth_provider
        u.username = 'nick%'
        assert 'nick' == u.nickname
        assert '' == u.auth_provider

    def test_can(self):
        r = Role(name='Can', permissions=0x09)
        r.save()
        u = UserFactory()
        u.set_role('Can')
        assert u.can(0x09)
        assert u.can(0x08)
        assert u.can(0x01)
        assert not u.can(0x05)
        assert not u.can(0x04)

    def test_is_administrator(self):
        u = UserFactory()
        assert u.role.name == 'User'
        assert not u.is_administrator()
        u.set_role('SiteAdmin')
        assert u.role.name == 'SiteAdmin'
        assert u.is_administrator()


@pytest.mark.usefixtures('db')
class TestAnonymousUser:
    """ Unit tests concerning the (anonymous user object"""

    def test_username(self):
        u = AnonymousUser()
        assert 'anonymous' == u.username

    def test_can(self):
        u = AnonymousUser()
        assert not 'anonymous' == u.can(0x00)

    def test_is_administrator(self):
        u = AnonymousUser()
        assert not u.is_administrator()


@pytest.mark.usefixtures('db')
class TestRole:
    """ Unit tests concerning the role object"""

    def test_role_create_default_and_print(self):
        r = Role(name='TestRole')
        r.save()
        assert 'TestRole' == r.name
        assert 0x00 ==  r.permissions
        assert False == r.default
        assert 'TestRole' in str(r)

    def test_role_names_are_unique(self):
        r = Role(name='TestRole')
        r.save()
        with pytest.raises(Exception):
            r = Role(name='TestRole')
            r.save()

    def test_role_create_details(self):
        r = Role(name='TestRole', permissions=0x01, default=True)
        assert 'TestRole' == r.name
        assert 0x01 ==  r.permissions
        assert True == r.default
        assert 'TestRole' in str(r)

    def test_list_of_role_names_and_insert_default(self):
        Role.insert_roles()
        role_names = Role.list_of_role_names()
        assert 2 == len(role_names)
        assert 'User' in role_names
        assert 'SiteAdmin' in role_names
        Role.insert_roles(True)
        role_names = Role.list_of_role_names()
        assert 3 == len(role_names)
        assert 'Admin' in role_names
