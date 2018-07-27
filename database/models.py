from sqlalchemy import Table, Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from flask_login import UserMixin, AnonymousUserMixin

Base = declarative_base()

userSearchers = Table('association', Base.metadata,
	Column('user_id', Integer, ForeignKey('user.id')),
	Column('search_id', Integer, ForeignKey('search.id'))
)

class User(Base, UserMixin):

	__tablename__ = 'user'
	
	id = Column(Integer, primary_key=True)
	email = Column(String)
	password = Column(String)
	account_type = Column(Integer)

	searchers = relationship("Search", secondary=userSearchers, cascade="save-update, merge, delete")

	def is_admin(self):
		return self.account_type > 0

	def __repr__(self):
		return "<User(email='{}')>".format(self.email)

class Anonymous(AnonymousUserMixin):
	
	def __init__(self):
		self.username = 'Guest'

	def is_admin(self):
		return False

class Search(Base):

	__tablename__ = 'search'
	
	id = Column(Integer, primary_key=True)
	url = Column(String)
	date_added = Column(DateTime)
	last_search = Column(DateTime)

	def __repr__(self):
		return "<Search(url='{}')>".format(self.url)