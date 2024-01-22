from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    date = Column(String, nullable=False)
    direction = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # def __repr__(self):
    #     return self.date

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, default=None, nullable=True)
    tg_id = Column(String, nullable=False)
    admin = Column(Boolean, default=False, nullable=False)
    premium = Column(Boolean, default=False, nullable=False)
    everyday_message = Column(Boolean, default=True)
    tickets = relationship(Ticket, backref='users', lazy=True)
    
    def __repr__(self):
        return self.tg_id
    
