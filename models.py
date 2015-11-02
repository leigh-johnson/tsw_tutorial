# -*- coding: utf-8> -*-
import base64
import uuid
import json
import hashlib
import copy
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy import String, Integer, Text, Enum, Table


### Database schema requires "None" be inserted into columns with null values
### Default "None" / "null" value can be accessed via Column(default='aDefaultValue) parameter

Base = declarative_base()

def Jsonify():
	_visited_objs = []
	class AlchemyEncoder(json.JSONEncoder):
		def default(self, obj):
			if isinstance(obj.__class__, DeclarativeMeta):
				# don't re-visit self
				if obj in _visited_objs:
					return None
				_visited_objs.append(obj)
				# an SQLAlchemy class
				fields = {}
				for field in [x for x in dir(obj) if not x.startswith(('__', '_sa', '_dec')) and x != 'metadata']:
					fields[field] = obj.__getattribute__(field)
				# a json-encodable dict
				return fields

			try:
				scrubbed = scrub(json.JSONEncoder.default(self, obj))
				return scrubbed
			except:
				pass
	return AlchemyEncoder

class Admin(Base):
	'''
	Admins are policy-permitted to POST, PUT, DELETE on access routes

	Policies & handlers on auth.py
	'''
	__tablename__ = 'admin'
	_id = Column(Integer, primary_key=True)
	username =  Column(String(16), unique=True)
	password = Column(String(16))
 

	@staticmethod
	def listByID(session):
		return session.query(Admin).all()

class Body_en(Base):
	'''Body exists so body_$language columns can contain many serialized entries
	
	e.g. body[0] & img[0] will share a CKeditor instance, if an img model is used.'''
	__tablename__ = 'body_en'
	_id = Column(Integer, primary_key=True)
	article_id = Column(Integer, ForeignKey('article._id', ondelete='CASCADE'))
	text = Column(Text)

	@staticmethod
	def list(session):
		return session.query(Body).all()

class Body_fr(Base):
	'''Body exists so body_$language columns can contain many serialized entries
	
	e.g. body[0] & img[0] will share a CKeditor instance'''
	__tablename__ = 'body_fr'
	_id = Column(Integer, primary_key=True)
	article_id = Column(Integer, ForeignKey('article._id', ondelete='CASCADE'))
	text = Column(Text)

	@staticmethod
	def list(session):
		return session.query(Body).all()

class Body_de(Base):
	'''Body exists so body_$language columns can contain many serialized entries
	
	e.g. body[0] & img[0] will share a CKeditor instance'''
	__tablename__ = 'body_de'
	_id = Column(Integer, primary_key=True)
	article_id = Column(Integer, ForeignKey('article._id', ondelete='CASCADE'))
	text = Column(Text)

	@staticmethod
	def list(session):
		return session.query(Body).all()

## Association table

tag_association = Table('tag_association', Base.metadata,
	Column('article_id', Integer, ForeignKey('article._id')),
	Column('tag_id', Integer, ForeignKey('tag._id'))
	)
class Tag(Base):
	__tablename__='tag'
	_id = Column(Integer, primary_key=True)
	title_en = Column(String(100))
	title_fr = Column(String(100))
	title_de = Column(String(100))

	@staticmethod
	def list(session):
		'''Returns an ordered list'''
		return session.query(Tag).all()

class Article(Base):
	__tablename__ = 'article'
	_id = Column(Integer, primary_key=True)
	layout = Column(String(100), default='default')
	icon = Column(String(100), default='icon-file-text')
	lua_tag = Column(Integer)
	is_public = Column(Boolean, default=False)
	order = Column(Integer)
	banner_src = Column(String(100), default="http://placehold.it/620x175/1e1e1e/ffffff/620x175&text=620x175px")
	video_src = Column(String(100))

	is_category = Column(Boolean, default=False)

	## If parent_id is _id, article is top level
	parent_id = Column(Integer, ForeignKey('article._id'))
	articles = relationship("Article", order_by='Article.order')

	## Many to many
	tags = relationship("Tag", secondary=tag_association, backref='articles')

	title_en = Column(String(35))
	body_en = relationship("Body_en", backref="article_en", cascade_backrefs=False, order_by='Body_en._id', passive_deletes=True)

	title_fr = Column(String(35))
	body_fr = relationship("Body_fr", backref="article_fr", order_by='Body_fr._id',passive_deletes=True)

	title_de = Column(String(35))
	body_de = relationship("Body_de", backref="article_de", order_by='Body_de._id',passive_deletes=True)

	@staticmethod
	def list(session):
		'''Returns an ordered list'''
		return session.query(Article).order_by(Article.order).all()

	def toDict():
		return dict((col, getattr(row, col)) for col in row.__table__.columns.keys())
