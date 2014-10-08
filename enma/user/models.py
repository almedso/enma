# -*- coding: utf-8 -*-
import datetime as dt

from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous  import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

from enma.extensions import bcrypt
from enma.database import (
    Column,
    db,
    Model,
    ReferenceCol,
    relationship,
    SurrogatePK,
)


class Permission:
    READ_USER = 0x01
    CREATE_USER = 0x02
    UPDATE_USER = 0x04
    DELETE_USER = 0x08

    READ_ORGANIZATION = 0x10
    CREATE_ORGANIZATION = 0x20
    UPDATE_ORGANIZATION = 0x40
    DELETE_ORGANIZATION = 0x80

    READ_ACTIVITY = 0x0100
    DELETE_ACTIVITY = 0x0200

    ADMINISTRATOR = 0xFFFFFFFF


class Role(SurrogatePK, Model):
    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    permissions = Column(db.Integer, default=0x00, nullable=False)
    default = Column(db.Boolean, default=False, unique=False, nullable=True)
    users = relationship('User', backref='role', lazy='dynamic')

    def __init__(self, *cargs, **kwargs):
        db.Model.__init__(self, *cargs, **kwargs)

    def __repr__(self):
        return '{name}'.format(name=self.name)

    @staticmethod
    def insert_roles():
        roles = {
                 'User' : (0x0000, True),
                 'Admin' : (Permission.CREATE_USER | Permission.UPDATE_USER |
                            Permission.READ_USER | Permission.DELETE_USER,
                            False),
                 'SiteAdmin' : (Permission.ADMINISTRATOR, False )
                 }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
            db.session.commit()


    @staticmethod
    def list_of_role_names():
        return map(lambda x: x.name, Role.query.all())


class User(UserMixin, SurrogatePK, Model):

    __tablename__ = 'users'
    username = Column(db.String(80), unique=True, nullable=False)
    email = Column(db.String(80), unique=True, nullable=False)
    email_validated = Column(db.Boolean(), default=False)

    #: Authentication and the hashed password
    password = Column(db.String(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=dt.datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)

    first_name = Column(db.String(40), nullable=True)
    last_name = Column(db.String(40), nullable=True)
    active = Column(db.Boolean(), default=False)
    role_id = Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, username, email, password=None, **kwargs):
        db.Model.__init__(self, username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps( (self.username) )

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            print 'data: ', str(data)
        except:
            return None
        return User.query.filter_by(username=data).first()

    @property
    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def __repr__(self):
        return '<User({username!r})>'.format(username=self.username)

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTRATOR)

    def set_role(self, name):
        role = Role.query.filter_by(name=name).first()
        if not role:
            raise Exception('Role %s does not exist' % name)
        self.role = role

    @property
    def nickname(self):
        try:
            return self.username.split('%')[0]
        except:
            return self.username

    @property
    def auth_provider(self):
        try:
            return self.username.split('%')[1]
        except:
            return 'not-set'


class AnonymousUser(AnonymousUserMixin):
    username = 'anonymous'
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
