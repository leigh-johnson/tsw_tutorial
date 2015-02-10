# -*- coding: utf-8> -*-
import base64
import uuid
import json
import hashlib
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.types import String, Integer, Text

Base = declarative_base()

### Database schema requires 'None' be inserted into columns with null values
### Default 'None' value can be accessed by declaring Column(default='aDefault') parameter

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
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                    fields[field] = obj.__getattribute__(field)
                # a json-encodable dict
                return fields

            try:
             	return json.JSONEncoder.default(self, obj)
            except:
            	pass
    return AlchemyEncoder

class Admin(Base):
	'''
	Admins are policy-permitted to POST, PUT, DELETE on access routes
	'''
	__tablename__ = 'admin'
	_id = Column(Integer, primary_key=True)
	username =  Column(String(16), unique=True)
	password = Column(String(16))
 

	@staticmethod
	def listByID(session):
		return session.query(Admin).all()

class Body(Base):
	'''Body exists so body_$language columns can contain many entries
	serialized with model.imgs[]
	e.g. body[0] & img[0] will share a CKeditor instance'''
	__tablename__ = 'body'
	_id = Column(Integer, primary_key=True)
	category_id = Column(Integer, ForeignKey('category._id'))
	article_id = Column(Integer, ForeignKey('article._id'))
	text = Column(Text)

	@staticmethod
	def list(session):
		return session.query(Body).all()


class Category(Base):
	'''
	title_en: LOC STRING
	description_en: LOC STRING
	body_en: LOC STRING
	'''
	__tablename__ = 'category'
	_id = Column(Integer, primary_key=True)
	parent_id = Column(Integer, ForeignKey('category._id'))
	articles = relationship("Article", backref="category", order_by='Article.order')
	imgs = relationship("Img", backref="category")
	layout = Column(String(35), default="default")
	order = Column(Integer)
	icon = Column(String(50))
	lua_tag = Column(Integer)
	publish = Column(Boolean)
	categories = relationship("Category", order_by='Category.order')

	title_en = Column(String(35))
	description_en = Column(String(255))
	body_en = relationship("Body", backref="category_en", order_by='Body._id')

	title_fr = Column(String(35))
	description_fr = Column(String(255))
	body_fr = relationship("Body", backref="category_fr", order_by='Body._id')

	title_de = Column(String(35))
	description_de = Column(String(255))
	body_de = relationship("Body", backref="category_de", order_by='Body._id')

	@staticmethod
	def list(session):
		return session.query(Category).all()

	def toDict():
		return dict((col, getattr(row, col)) for col in row.__table__.columns.keys())



class Article(Base):
	'''
	title_en: LOC STRING
	description_en: LOC STRING
	body_en: LOC STRING
	'''
	__tablename__ = 'article'
	_id = Column(Integer, primary_key=True)
	category_id = Column(Integer, ForeignKey('category._id'))
	imgs = relationship("Img", backref="article", order_by='Img._id')
	video = relationship("Video", backref="article", order_by='Video._id')
	layout = Column(String(35), default="default")
	order = Column(Integer)
	lua_tag = Column(Integer)
	publish = Column(Boolean)

	title_en = Column(String(35))
	description_en = Column(String(255))
	body_en = relationship("Body", backref="article_en", order_by='Body._id')

	title_fr = Column(String(35))
	description_fr = Column(String(255))
	body_fr = relationship("Body", backref="article_fr", order_by='Body._id')

	title_de = Column(String(35))
	description_de = Column(String(255))
	body_de = relationship("Body", backref="article_de", order_by='Body._id')


	@staticmethod
	def list(session):
		return session.query(Article).all()


class Img(Base):
	'''
	NO LOCALIZED STRINGS
	title for internal use only
	'''
	__tablename__ = 'img'
	_id = Column(Integer, primary_key=True)
	category_id = Column(Integer, ForeignKey('category._id'))
	article_id = Column(Integer, ForeignKey('article._id'))
	src = Column(String(35))
	title = Column(String(55))

	@staticmethod
	def list(session):
		return session.query(Img).all()

class Video(Base):
	'''
	NO LOCALIZED STRINGS
	title for internal use only
	'''
	__tablename__ = 'video'
	_id = Column(Integer, primary_key=True)
	category_id = Column(Integer, ForeignKey('category._id'))
	article_id = Column(Integer, ForeignKey('article._id'))
	src = Column(String(35))
	title = Column(String(55))

	@staticmethod
	def list(session):
		return session.query(Video).all()