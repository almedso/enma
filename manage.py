#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import MigrateCommand
from flask.ext.assets import ManageAssets


from enma.app import create_app
from enma.user.models import User, Role
from enma.settings import DevConfig, ProdConfig
from enma.database import db
from enma.user.admin import establish_admin_defaults
from enma.assets import assets

if os.environ.get("ENMA_ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

manager = Manager(app)
TEST_CMD = "py.test tests"

def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db, 'User': User, 'Role': Role}


@manager.command
def test(slow=False, mail=False):
    """Run the tests."""
    import pytest
    command_args = ['tests', '--verbose', '--cov-report', 'xml',
                    '--cov', 'enma', '--junitxml', 'unittest.xml']
    if mail:
        command_args.append("--mail")
    if slow:
        command_args.append("--slow")
    exit_code = pytest.main(command_args)
    return exit_code


@manager.command
def set_initial_data():
    """ Create or update all initial data.

    The initial data is a set of Role definitions and
    Software definitions.
    """
    Role.insert_roles()  # make sure we have all roles available


@manager.command
def set_admin(reset_password=False):
    """
    Create the admin user or reset the admin to factory defaults
    I.e. the admin user has the role 'SiteAdmin'.
    The password is (re-)set optionally to '_admin'

    :param reset_password: if True the admin password will be reset to '_admin'
    """
    Role.insert_roles()  # make sure we have all roles available
    establish_admin_defaults(reset_password=reset_password)

manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()