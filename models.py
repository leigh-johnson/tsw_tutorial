import base64
import uuid
import hashlib
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.types import String, Integer, Text

Base = declarative_base()

### Database schema requires 'None' be inserted into columns with null values
### Default 'None' value can be accessed by declaring Column(default='aDefault') parameter

class Admin(Base):
	'''
	Admins are policy-permitted to POST, PUT, DELETE on access routes
	'''
	__tablename__ = 'admin'
	id = Column(Integer, primary_key=True)
	username =  Column(String)
	password = Column(String)
 
	def __init__(self, username, password):
		Base.__init__(self)
		self.username = username
		self.password = self.hash_password(password)
		# generate salt
		# salt the password

	def hash_password(password, salt=None):
		if salt is None:
			salt = uuid.uuid4().hex

		hashed_password = hashlib.sha512(password + salt).hexdigest()
		return (hashed_password, salt)

	def verify_password(password, hashed_password, salt):
		re_hashed, salt = hash_password(password, salt)

		return re_hashed == hashed_password

		@staticmethod
		def list(session):
				return session.query(Admin).all()

class Category(Base):
	'''
	title_en: LOC STRING
	description_en: LOC STRING
	body_en: LOC STRING
	'''
	__tablename__ = 'category'
	id = Column(Integer, primary_key=True)
	articles = relationship("Article", backref="category")
	imgs = relationship("Img", backref="category")

	title_en = Column(String(35))
	description_en = Column(String(255))
	body_en = Column(Text)

	title_fr = Column(String(35))
	description_fr = Column(String(255))
	body_fr = Column(Text)

	title_de = Column(String(35))
	description_de = Column(String(255))
	body_de = Column(Text)

	def __init__(self, **kwargs):
		Base.__init__(self)
		for key, value in kwargs.iteritems():
			self.key = value

	@staticmethod
	def list(session):
		return session.query(Category).all()

class Article(Base):
	'''
	title_en: LOC STRING
	description_en: LOC STRING
	body_en: LOC STRING
	'''
	__tablename__ = 'article'
	id = Column(Integer, primary_key=True)
	category_id = Column(Integer, ForeignKey('category.id'))
	imgs = relationship("Img", backref="article.id")
	layout = Column(String)

	title_en = Column(String(35))
	description_en = Column(String(255))
	body_en = Column(Text)

	title_fr = Column(String(35))
	description_fr = Column(String(255))
	body_fr = Column(Text)

	title_de = Column(String(35))
	description_de = Column(String(255))
	body_de = Column(Text)


	def __init__(self, **kwargs):
		Base.__init__(self)
		for key, value in kwargs.iteritems():
			self.key = value

	@staticmethod
	def list(session):
		return session.query(Article).all()

class Img(Base):
	'''
	NO LOCALIZED STRINGS
	title for internal use only
	'''
	__tablename__ = 'img'
	id = Column(Integer, primary_key=True)
	category_id = Column(Integer, ForeignKey('category.id'))
	article_id = Column(Integer, ForeignKey('article.id'))
	src = Column(String)
	title = Column(String(55))


	def __init__(self, **kwargs):
		Base.__init__(self)
		for key, value in kwargs.iteritems():
			self.key = value

	@staticmethod
	def list(session):
		return session.query(Img).all()
