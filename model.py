from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base is the instance of declarative_base class
Base = declarative_base()


class User(Base):
    """User is inherited from Base class, which is the instance
    of declarative_base. it is used to create user table
    and map the table acording to given atributes"""

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Catagory(Base):
    """Catagory is inherited from Base class, which is the instance
        of declarative_base. it is used to create catagory table
        and map the table acording to given atributes"""

    __tablename__ = 'catagory'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Item(Base):
    """Item is inherited from Base class, which is the instance
        of declarative_base. it is used to create item table
        and map the table acording to given atributes"""

    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    catagory_id = Column(Integer, ForeignKey('catagory.id'))
    catagory = relationship(Catagory)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
        }


engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.create_all(engine)
