from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension
import transaction

import ziggurat_foundations.models
from ziggurat_foundations.models import BaseModel, UserMixin, GroupMixin
from ziggurat_foundations.models import GroupPermissionMixin, UserGroupMixin
from ziggurat_foundations.models import GroupResourcePermissionMixin, ResourceMixin
from ziggurat_foundations.models import UserPermissionMixin, UserResourcePermissionMixin
from ziggurat_foundations.models import ExternalIdentityMixin
from ziggurat_foundations import ziggurat_model_init

from pyramid.security import (
    Allow,
    Authenticated,
    Everyone,
    )


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Group(GroupMixin, Base):
    pass

class GroupPermission(GroupPermissionMixin, Base):
    pass


class UserGroup(UserGroupMixin, Base):
    @classmethod
    def get_by_email(cls, email):
        user = User.get_by_email(email)
        return cls.get_by_user(user)
        
    @classmethod
    def _get_by_user(cls, user):
        return DBSession.query(cls).filter_by(user_id=user.id).all()
        
    @classmethod
    def get_by_user(cls, user):
        groups = []
        for g in cls._get_by_user(user):
            groups.append(g.group_id)
        return groups
                
    @classmethod
    def set_one(cls, session, user, group):
        member = DBSession.query(cls).filter_by(user_id=user.id, group_id=group.id)
        try:
            member = member.one()
        except NoResultFound:
            member = cls(user_id=user.id, group_id=group.id)
            DBSession.add(member)
            transaction.commit()
        
    @classmethod
    def set_all(cls, user, group_ids=[]):
        if type(user) in [StringType, UnicodeType]:
            user = User.get_by_email(user)
        olds = cls._get_by_user(user)
        news = []
        for group_id in group_ids:
            group = DBSession.query(Group).get(group_id)
            member = cls.set_one(user, group)
            news.append(group)
        for old in olds:
            if old not in news:
                old.delete()
                DBSession.commit()
                
    @classmethod
    def get_by_group(cls, group):
        users = []
        for g in DBSession.query(cls).filter_by(group=group):
            users.append(g.user)
        return users                


class GroupResourcePermission(GroupResourcePermissionMixin, Base):
    pass

class Resource(ResourceMixin, Base):
    pass

class UserPermission(UserPermissionMixin, Base):
    pass

class UserResourcePermission(UserResourcePermissionMixin, Base):
    pass


class User(UserMixin, Base):
    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = self.set_password(password)

    password = property(_get_password, _set_password)

    @classmethod
    def get_by_email(cls, email):
        return DBSession.query(cls).filter_by(email=email).first()
            
    def get_groups(self):
        return UserGroup.get_by_user(self)


class ExternalIdentity(ExternalIdentityMixin, Base):
    pass


class RootFactory(object):
    def __init__(self, request):
        self.__acl__ = [
            (Allow, Authenticated, 'view'),
            (Allow, Authenticated, 'edit'),
            (Allow, 'Admin', 'view'),
            (Allow, 'Admin', 'edit'),
            (Allow, 'Staff', 'view'),
            ]

def init_model():
    ziggurat_model_init(User, Group, UserGroup, GroupPermission, UserPermission,
                   UserResourcePermission, GroupResourcePermission, Resource,
                   ExternalIdentity, passwordmanager=None)


##################        
# Initialization #
##################
def create_anonymous():
    email = 'anonymous@local'
    try:
        return DBSession.query(User).filter_by(email=email).one()
    except NoResultFound:
        from random import randrange    
        user = User(email=email)
        user.password = str(randrange(100000, 999999))
        user.status = 1
        user.id = 0
        DBSession.add(user)
        DBSession.flush()
    return user
    
def create_admin():
    email = 'admin@local'
    try:
        return DBSession.query(User).filter_by(email=email).one()
    except NoResultFound:
        user = User(email=email)
        user.password = 'admin'
        user.status = 1
        DBSession.add(user)
        DBSession.flush()
    return user    

def init_db():
    create_anonymous()
    user = create_admin()
    groups = [('Admin', 'Can change'),
              ('Staff', 'Read only'),
             ]
    for name, desc in groups:
        try:
            group = DBSession.query(Group).filter_by(group_name=name).one()
        except NoResultFound:
            group = Group(group_name=name, description=desc)
            DBSession.add(group)
            DBSession.flush()
    # Register admin@local to Admin group
    user_group = DBSession.query(UserGroup).filter_by(user_id=user.id,
                                                      group_id=group.id)
    try:
        user_group = user_group.one()
    except NoResultFound:
        user_group = UserGroup(user_id=user.id, group_id=group.id)
        DBSession.add(user_group)
        DBSession.flush()
    transaction.commit()
