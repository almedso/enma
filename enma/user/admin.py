# -*- coding: utf-8 -*-
from enma.user.models import User, Role, Permission
from enma.public.domain import compose_username
from enma.database import db

def establish_admin_defaults(reset_password=True):
    """ Set the admin user to SiteAdmin, and optionally set the password

    If the admin user does not exist he/she is created with minimal data.
    The password will be '_admin' in case it is set.

    :param reset_password: if True the password will be set otherwise not
           The password will be set if no parameter given.
    """
    username = compose_username('admin', None, 'local')
    admin = User.query.filter(User.username==username).first()
    if not admin:
        admin = User(username=username, email='info@pixmeter.eu',
                     password='admin', active=True,
                     first_name='Site', last_name='Administrator')
    if reset_password:
        admin.set_password('admin')
    admin.active = True
    admin.role = Role.query.filter(Role.name=='SiteAdmin').first()
    if not admin.role:
        admin.role = Role('SiteAdmin', permissions=Permission.ADMINISTRATOR)
    db.session.add(admin)
    db.session.commit()
