# -*- coding: utf-8> -*-
import base64
import uuid
import json
import hashlib
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.types import String, Integer, Text, Enum

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
	article_id = Column(Integer, ForeignKey('article._id'))
	text = Column(Text)

	@staticmethod
	def list(session):
		return session.query(Body).all()


class Article(Base):
	__tablename__ = 'article'
	_id = Column(Integer, primary_key=True)
	layout = Column(Enum('default', 'video', 'img_hero'), default='default')
	icon = Column(String(50))
	lua_tag = Column(Integer)
	public = Column(Boolean)
	order = Column(Integer)

	is_category = Column(Boolean, default=True)
	## If parent_id is _id, article is top level
	parent_id = Column(Integer, ForeignKey('article._id'))
	articles = relationship("Article", order_by='Article.order')


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

	def toDict():
		return dict((col, getattr(row, col)) for col in row.__table__.columns.keys())
