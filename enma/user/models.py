# -*- coding: utf-8 -*-
"""
Module: User (and related) data and domain models
"""
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
    """ Mapping of a symbolic name to a permission integer

    Constraints:
       this is a single place to define permissions
       extensions should inherit from this class definitions

    """
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
    """ A role is composed by a set of permissions and assigns a name to it.

    Attributes:
      name (str): The name of the role.
      permissions (int): or-ed field of permissions
      default (boolean): Is true for only one Role (i.e. user).

    """
    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    permissions = Column(db.Integer, default=0x00, nullable=False)
    default = Column(db.Boolean, default=False, unique=False, nullable=False)
    users = relationship('User', backref='role', lazy='dynamic')

    def __init__(self, *cargs, **kwargs):
        db.Model.__init__(self, *cargs, **kwargs)

    def __repr__(self):
        return '{name}'.format(name=self.name)

    @staticmethod
    def insert_roles(admin=False):
        """ Populate the database with initial roles

        Provide a default user that who gets no rights at all
        Provide a super admin (siteadmin) who is allowed to do anything.

        Args:
            admin (boolean): is optional if not given false, adds an admin
               role which allows to manage users
        """
        roles = {
                'User' : (0x0000, True),  # default user
                'SiteAdmin' : (Permission.ADMINISTRATOR, False )  # super admin
                }
        if admin:  # add just another role
            roles['Admin'] = ( (Permission.CREATE_USER | Permission.UPDATE_USER |
                            Permission.READ_USER | Permission.DELETE_USER,
                            False) )

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
        """ List all possible role names

        Returns:
            List of strings: of role names
        """
        return map(lambda x: x.name, Role.query.all())


class User(UserMixin, SurrogatePK, Model):
    """ The User data model

    The username is composed of the nickname, a delimieter (%) and
    the authentication provider. For local authentication method, this
    provider is set to 'local' and a password is set, for any OpenId
    Authentication provider the OpenId URL is used as the authentication
    provider.

    Attributes:
        username (str): The login name of the user (long form) - unique.
        email (str): The email address to contact the user.
        email_validated (bool): Flag if the email address has been validated.
        password (str): bcryped (hashed and salted) user password - Only
          set for local users
        created_at (timestamp): When was the user created/registered
        last_seen (timestamp): Last time the user logged in
        confirmed (boolean): 
        first_name (str): First name of the user
        last_name (str): Last name of the user
        active (boolean): Only active user can log in.
        role: Reference to the users Role

    """

    __tablename__ = 'users'
    username = Column(db.String(80), unique=True, nullable=False)
    email = Column(db.String(80), unique=True, nullable=False)
    email_validated = Column(db.Boolean(), default=False)

    #: Authentication and the hashed password
    password = Column(db.String(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=dt.datetime.utcnow)

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
        """ Set the users password

        Agrs:
           password (str): the users new password
        """
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """ Check if the passwords matches the users password

        Agrs:
           password (str): the password to check
        """
        return bcrypt.check_password_hash(self.password, value)

    def generate_auth_token(self, expiration):
        """ Generate a token, that is sufficient for authentication

        This token can be used to authenticate, i.e. it is a random string
        that encodes the user and a expiration timestamp

        Args:
            expiration (timestamp): The expiration timestamp
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps( (self.username) )

    @staticmethod
    def verify_auth_token(token):
        """ Verify an authentication token

        Returns:
            User object: if and only if the token is valid and not expired
            It is not checked if the user is active.
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.filter_by(username=data).first()

    @property
    def full_name(self):
        """ The users full name """
        return "{0} {1}".format(self.first_name, self.last_name)

    def __repr__(self):
        return '<User({username!r})>'.format(username=self.username)

    def can(self, permissions):
        """ Check if a user has a set of permissions

        Args:
            permissions (int): or-ed set of permissions to check
        Returns:
            boolean: True if the user has *all* permissions
        """
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        """ Check if the user is the super administrator

        Returns:
            Boolean: True if and only if the user has the role 'SiteAdmin'
        """
        return self.can(Permission.ADMINISTRATOR)

    def is_locally_authenticated(self):
        """ Check if the user authenticates locally (using the password)

        Returns:
            Boolean: True if local authentication method is chosen
        """
        return 'local' == self.auth_provider

    def set_role(self, name):
        """ Assigns a new role to the user

        Args:
            name (str): The name of the user role
        Raises:
            Exception: If the role with the name name does not exist
        """
        role = Role.query.filter_by(name=name).first()
        if not role:
            raise Exception('Role %s does not exist' % name)
        self.role = role

    @property
    def nickname(self):
        """ The (short) username reduced by the authentication provider """
        try:
            return self.username.split('%')[0]
        except:
            return self.username

    @property
    def auth_provider(self):
        """ The authentication provider """
        try:
            return self.username.split('%')[1]
        except:
            return 'not-set'


class AnonymousUser(AnonymousUserMixin):
    """ Anonymous User to be used if no user has been logged in. """
    username = 'anonymous'
    def can(self, permissions):
        """ Check if a user has a set of permissions

        Args:
            permissions (int): or-ed set of permissions to check
        Returns:
            boolean: Always false
        """
        return False

    def is_administrator(self):
        """ Check if the user is the super administrator

        Returns:
            Boolean: Always false
        """
        return False

    def is_locally_authenticated(self):
        """ Check if the user is locally authenticated

        Returns:
            Boolean: Always false
        """