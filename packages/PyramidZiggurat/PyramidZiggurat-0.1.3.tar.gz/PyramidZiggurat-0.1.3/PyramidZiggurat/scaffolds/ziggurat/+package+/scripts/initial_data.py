import transaction
from factory.alchemy import SQLAlchemyModelFactory

from ..models import (
    DBSession,
    User,
    Group,
    )

# https://factoryboy.readthedocs.org/
class BaseFactory(SQLAlchemyModelFactory):
    FACTORY_SESSION = DBSession
    

#########
# Users #
#########
class UserFactory(BaseFactory):
    FACTORY_FOR = User
    
class Anonymous(UserFactory):
    id = 0
    email = 'anonymous@local'
    user_name = 'anonymous'
    status = 0

class Admin(UserFactory):
    id = 1
    email = 'admin@local'
    user_name = 'admin'
    password = 'admin'
    status = 1


#########
# Group #
#########
class GroupFactory(BaseFactory):
    FACTORY_FOR = Group

class Administrator(GroupFactory):
    id = 1
    group_name = 'Admin'
    description = 'Can change'
    
class Staff(GroupFactory):
    id = 2
    group_name = 'Staff'
    description = 'Read only'
    

#########
# Tools #
#########
def save(cls):
    data = cls.build()
    row = DBSession.query(cls.FACTORY_FOR).filter_by(id=data.id).first()
    if not row:
        row = cls()
        
def save_all(list_of_class):
    for cls in list_of_class:
        save(cls)

def set_sequence(orm):
    row = DBSession.query(orm).order_by('id DESC').first()
    last_id = row.id
    seq_name = '%s_id_seq' % orm.__tablename__
    sql = "SELECT setval('%s', %d)" % (seq_name, last_id)
    engine = DBSession.bind    
    engine.execute(sql)
    
def set_sequences(list_of_orm):
    for orm in list_of_orm:
        set_sequence(orm)

def insert():
    save_all([Anonymous, Admin, Administrator, Staff])
    set_sequences([User, Group])
    transaction.commit()
