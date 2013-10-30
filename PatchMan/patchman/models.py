"""
"""
from datetime import datetime
from sqlalchemy import engine_from_config
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (backref, relationship, scoped_session, sessionmaker)
from sqlalchemy.orm.interfaces import MapperExtension
from sqlalchemy.schema import (Column, ForeignKey)
from sqlalchemy.types import (Integer, String, Boolean, DateTime, TEXT, Unicode)
from zope.sqlalchemy import ZopeTransactionExtension
import transaction

'''
from sqlalchemy.dialects.sqlite import 
                    BLOB, BOOLEAN, CHAR, DATE, DATETIME, DECIMAL, FLOAT, \
                                INTEGER, NUMERIC, SMALLINT, TEXT, TIME, TIMESTAMP, \
                                            VARCHAR
'''


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class BaseExtension(MapperExtension):  
    """Base entension class for all entities """  
  
    def before_insert(self, mapper, connection, instance):  
        """ set the created_at  """  
        instance.created_at = datetime.now()  
  
    def before_update(self, mapper, connection, instance):  
        """ set the updated_at  """  
        instance.updated_at = datetime.now()
        

class BaseEntity(object):  
   # for before insert before update base extension class  
    __mapper_args__ = { 'extension': BaseExtension() }    


class Brand(Base, BaseEntity):  
    """Brand entity class """  
    __tablename__ = 'brand'  
  
    id = Column(Integer, primary_key=True)  
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime)  
    updated_at = Column(DateTime)  
  
    def __init__(self,  name=""):  
        self.name = name
        
class Device(Base, BaseEntity):  
    """Device entity class """  
    __tablename__ = 'devices'  
  
    id = Column(Integer, primary_key=True)  
    name = Column(String(100), nullable=False, unique=True)
    ip = Column(String(100), nullable=False, unique=True)
    username = Column(String(55), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime)  
    updated_at = Column(DateTime)  
  
    def __init__(self,  name=""):  
        self.name = name
      
    @classmethod
    def first(cls):
        return DBSession.query(Device).first()
   
class Plate(Base, BaseEntity):
    """Plate entity class """
    __tablename__ = 'plates'
    
    id = Column(Integer, primary_key=True) 
    code = Column(String(6), nullable=False, unique=True)
    active = Column(Boolean, nullable=False, default=True)
    # foreing key
    brand_id = Column(Integer, ForeignKey('brand.id', 
        name="fk_plate_brand", onupdate='CASCADE', ondelete='RESTRICT'), nullable=True)
    brand = relationship("Brand")
    notes = Column(TEXT)
    created_by_user = Column(String(50))  
    created_at = Column(DateTime)  
    updated_by_user = Column(String(50))  
    updated_at = Column(DateTime)  
    logs  = relationship("PlateLog", order_by="desc(PlateLog.id)", backref="plate")
    
    def __init__(self, code="", brand_id=0, active=True, notes=""):
        self.code = code
        self.brand_id = brand_id
        self.active = active
        self.notes = notes

    def __repr__(self):
        return "<Plate('%s - %i')>" % (self.code, int(self.active))

class PlateLog(Base, BaseEntity):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    plate_id = Column(Integer, ForeignKey('plates.id'))
    created_at = Column(DateTime)  
    updated_at = Column(DateTime)  
   
    def __init__(self):
        self.timestamp = datetime.now()
    def __repr__(self):
        return "<Log('%s')>" %(self.timestamp)

    def __json__(self, request):
        return {'t':self.timestamp.isoformat(),'p':self.plate.code}


class User(Base, BaseEntity):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(55), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    last_logged = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime)  
    updated_at = Column(DateTime)  
    
    @classmethod
    def by_name(cls, name):
        return DBSession.query(User).filter(User.name == name).first()
    
    def verify_password(self, password):
        return self.password == password


def populate():
    """add default data to tables """
    try:
        transaction.begin()
        dbsession = DBSession()
        dbsession.add_all([
                           Brand("Toyota"), 
                           Brand("Ford"), 
                           Brand("Chevrolet")
                           ])
        transaction.commit()
    except IntegrityError:
        transaction.abort()
    

def initialize_sql(settings):
    engine = engine_from_config(settings, "sqlalchemy.")
    DBSession.configure(bind=engine)
#    Base.metadata.bind = engine
#    Base.metadata.create_all(engine)
#    populate()
    