from sqlalchemy import Table, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import orm
from flask_login import UserMixin, AnonymousUserMixin

Base = declarative_base()

userSearchers = Table('user_search', Base.metadata,
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

searchAd = Table('search_ad', Base.metadata,
	Column('search_id', Integer, ForeignKey('search.id')),
	Column('ad_id', Integer, ForeignKey('ad.id'))
)

class Search(Base):

	__tablename__ = 'search'
	
	id = Column(Integer, primary_key=True)
	url = Column(String)
	date_added = Column(DateTime)
	last_search = Column(DateTime)
	last_sent = Column(DateTime)

	ads = relationship("Ad", secondary=searchAd, cascade="save-update, merge, delete")

	def __repr__(self):
		return "<Search(url='{}')>".format(self.url)

class Options(Base):

	__tablename__ = 'options'
	
	id = Column(Integer, primary_key=True)
	plugin_name = Column(String)
	key = Column(String)
	value = Column(String)

	def __repr__(self):
		return "<Option(plugin_name='{}', key='{}', value='{}')>".format(self.plugin_name, self.key, self.value)

class Ad(Base):

	__tablename__ = 'ad'

	id = Column(Integer, primary_key=True)
	title = Column(String)
	description = Column(String)
	url = Column(String)
	image_url = Column(String)
	price = Column(Float)
	ad_added = Column(DateTime)
	time_added = Column(DateTime)

	def __repr__(self):
		return "<Ad(title='{}', url='{}')>".format(self.title, self.url)