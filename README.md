# TSW Tutorials

## Dependencies

* [Peewee ORM](https://github.com/coleifer/peewee)

I chose to use an ORM for easy additions to the data models in future versions. A developer can extend a model like so:

```
from peewee import *

myDB = peewee.mySQLDatabase("mydb", host="hostname", port=3306, user="user", passwd="password")

class ThisSQLModel(peewee.Model):
	"""The root of our model, a SQL database"""
	class Meta:
		database = myDB

class Category(peewee.Model):
	"""mydb.Category table"""
	# Fields describe the mapping of models
	title = TextField()
	dateUpdated = DateTimeField()
	# A ForeignKeyField is a relationship to another model
	article = ForeignKeyField(Article, related_name='articles')



```

 [Peewee's documentation](http://docs.peewee-orm.com/) is comprehensive, the library is actively maintained, and numerous use cases are supplied as examples.  