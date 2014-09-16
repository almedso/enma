# -*- coding: utf-8 -*-
from enma.user.models import User, Role
from enma.public.domain import compose_username
from enma.database import db


def establish_all_roles_and_get_site_admin_role():
    Role.insert_roles()
    return Role.query.filter(Role.name=='SiteAdmin').first()


def establish_admin_defaults():
    """
    Reset the password of the admin user to admin.
    If the admin user does not exist he/she is created with minimal data.
    """
    username = compose_username('admin', None, 'local')
    admin = User.query.filter(User.username==username).first()
    if not admin:
        admin = User(username=username, email='admin@dummy.com',
                     password='admin', active=True,
                     first_name='Site', last_name='Administrator')
    else:
        admin.set_password('admin')
        admin.active = True
    admin.role = establish_all_roles_and_get_site_admin_role() 
    db.session.add(admin)
    db.session.commit()
