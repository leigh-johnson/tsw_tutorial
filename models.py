import base64
import uuid
import hashlib
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import String, Integer

Base = declarative_base()

class Admin(Base):
	'''
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

	'''
	__tablename__ = 'category'
	id = Column(Integer, primary_key=True)
	title_en = Column(String)
	articles = relationship("Articles", backref="parent")

class Article(Base):
	'''
	'''
	__tablename__ = 'article'
	id = Column(Integer, primary_key=True)
	category_id = Column(Integer, ForeignKey('category.id'))