# -*- coding: utf-8 -*-
""" Data and domain model for activities """
import datetime as dt

from enma.database import (
    Column,
    db,
    Model,
    SurrogatePK,
)
from flask_login import current_user
from flask import request
from enma.user.models import User, AnonymousUser

"""
Limit the set of possible categories to fixed meaningful subset
Keep it extensible by deriving from this class
"""

EMPTY = 0x00
AUTHENTICATION = 0x01
PRIVILEGE = 0x02
API = 0x04
USER = 0x08
IMPORT = 0x10
EXPORT = 0x20

categories =  {
               EMPTY : '',
               AUTHENTICATION : 'Authentication',
               PRIVILEGE : 'Privilege',
               API : 'RestAPI',
               USER : 'User',
               IMPORT : 'Import',
               EXPORT : 'Export',
               }


class Activity(SurrogatePK, Model):
    """
    An activity is reduced by all references on the database, it contains
    all data in plain text (copied or extracted). Reason: Recording an
    activity happens at a specific point in time and where the data model
    has a specific state. The recording should not be dependent on future data
    model state changes.
    """
    __tablename__ = 'activities'
    timestamp = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    actor = Column(db.String(80), nullable=False)
    category = Column(db.String(20), nullable=False, default='')
    acted_on = Column(db.String(80), nullable=False, default='')
    description = Column(db.String(128), nullable=False)
    origin = Column(db.String(40), nullable=False, default='')

    def __init__(self, actor, description, category=EMPTY, acted_on='',
                 origin='', **kwargs):
        db.Model.__init__(self, actor=actor, description=description,
                          category=categories[category],
                          acted_on=acted_on, origin=origin, **kwargs)

    def __repr__(self):
        return '{timestamp} {actor} {description}'.format(
                timestamp=self.timestamp, actor=self.actor,
                description=self.description)


def record(description, category=EMPTY, acted_on=None):
    """ General recording of an business relevant activity

    Determines actor and host automatically; 
    Transforms acted_on to a string (if given)
    Writes to the activity table

    Args:
        description (str): The description
        category (str): The category to record - fixed set of values only
        acted_on (str): Optional - the user or users data that is affected.
    """
    user = current_user  # get the current user
    acted_on_name = ''
    if acted_on and isinstance(acted_on, User):
        acted_on_name = acted_on.username
    # origin = request.remote_addr
    origin = 'not set' 
    if 'REMOTE_ADDR' in request.environ.keys():
        origin = request.environ['REMOTE_ADDR']
    act = Activity(user.username, description, category, acted_on_name, origin)
    db.session.add(act)
    db.session.commit()


def record_authentication(description='Login'):
    record(description, category=AUTHENTICATION)


def record_priviledge(acted_on, description='Change'):
    record(description, category=PRIVILEGE, acted_on=acted_on)


def record_api(description, acted_on=None):
    record(description, category=API, acted_on=acted_on)


def record_user(description, acted_on=None):
        record(description, category=USER, acted_on=acted_on)
