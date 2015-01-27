import os, os.path
import pymysql
import json
import cherrypy
from models import Base, Article, Category, Img, Admin
from cherrypy.process import wspbus, plugins


### Mako Templates ###
from mako.template import Template
from mako.lookup import TemplateLookup

lookup = TemplateLookup(directories=["view"])

### Plugins ###

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

        
class SAEnginePlugin(plugins.SimplePlugin):
    def __init__(self, bus):
        """
        The plugin is registered to the CherryPy engine and therefore
        is part of the bus (the engine *is* a bus) registery.
 
        We use this plugin to create the SA engine. At the same time,
        when the plugin starts we create the tables into the database
        using the mapped class of the global metadata.
 
        Finally we create a new 'bind' channel that the SA tool
        will use to map a session to the SA engine at request time.
        """
        plugins.SimplePlugin.__init__(self, bus)
        self.sa_engine = None
        self.bus.subscribe("bind", self.bind)
 
    def start(self):
        db_path = os.path.abspath(os.path.join(os.curdir, 'my.db'))
        self.sa_engine = create_engine('sqlite:///%s' % db_path, echo=True)
        Base.metadata.create_all(self.sa_engine)
 
    def stop(self):
        if self.sa_engine:
            self.sa_engine.dispose()
            self.sa_engine = None
 
    def bind(self, session):
        session.configure(bind=self.sa_engine)
 
class SATool(cherrypy.Tool):
    def __init__(self):
        """
        The SA tool is responsible for associating a SA session
        to the SA engine and attaching it to the current request.
        Since we are running in a multithreaded application,
        we use the scoped_session that will create a session
        on a per thread basis so that you don't worry about
        concurrency on the session object itself.
 
        This tools binds a session to the engine each time
        a requests starts and commits/rollbacks whenever
        the request terminates.
        """
        cherrypy.Tool.__init__(self, 'on_start_resource',
                               self.bind_session,
                               priority=20)
 
        self.session = scoped_session(sessionmaker(autoflush=True,
                                                  autocommit=False))
 
    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('on_end_resource',
                                      self.commit_transaction,
                                      priority=80)
 
    def bind_session(self):
        cherrypy.engine.publish('bind', self.session)
        cherrypy.request.db = self.session
 
    def commit_transaction(self):
        cherrypy.request.db = None
        try:
            self.session.commit()
        except:
            self.session.rollback()  
            raise
        finally:
            self.session.remove()

### Decorators ###

from functools import wraps
from cherrypy import response, expose


def jsonify(func):
    '''JSON decorator reponse headers'''
    @wraps(func)
    def wrapper(*args, **kw):
        cherrypy.response.headers["Content-Type"] = "application/json"        
    return wrapper

### App Index/Home/Root ### 
class RootController(object):

    @cherrypy.expose
    @jsonify
    def index(self):
        # Localization thread variable
        # Return tutorial categories, progress indicator, faction stylesheets
        categories = [category for category in Category.list(cherrypy.request.db)]
        template = lookup.get_template("index.html")
        return template.render(categories=categories, layout='default')

    def category(self):
        pass

    def article(self):
        pass

    def login(self):
        pass


### RESTful API Controllers ###
### ALL RETURNS ON API ROUTES AGONOSTICALLY RETURN `result` ###

class CategoryAPI(object):

    exposed = True

    @jsonify
    def GET(self, category_id=None):
        '''
        Returns category_id if id is supplied OR
        all category records if no id is supplied
        '''
        if category_id == None:
            result = [category for category in Category.list(cherrypy.request.db)]
            return result
        else: 
            result = cherrypy.request.db.query(Category).get(category_id)
            return result

    def POST(self, **kwargs):
        '''If authorized, persist a new Category() to session and return it
        No validation strategy implemented, use with caution
        '''
        result = Category(**kwargs)
        cherrypy.request.db.add(result)
        return result

    def PUT(self, **kwargs):
        '''If authorized, persist .update() on session
        **KWARGS:
        key=value
        No validation strategy implemented, use with caution
        '''
        values = {}
        for key, value in kwargs.iteritems():
            values[key] = value
        category_id = values[category_id]
        result = cherrypy.request.db.query(Category).filter(id == category_id).update(values)
        return result

    def DELETE(self, category_id):
        '''Marks object for delete in session
        Cascade should NEVER be handled in the Controllers
        Instead, declaratively state cascadence in model parameters'''
        result = cherrypy.request.db.query(Category).filter(id == category_id).delete()
        return result

class ArticleAPI(object):
    
    exposed = True

    def GET(self, category_id=None):
        '''Returns an article_id if supplied OR
        all article records if no id is supplied
        '''
        pass

    def POST(self, **kwargs):
        pass

    def PUT(self, **kwargs):
        '''If Authorized'''
        pass

    def DELETE(self, category_id):
        pass


class ImgAPI(object):

    exposed = True

    def GET(self, img_id=None):
        pass

    def POST(self, **kwargs):
        pass

    def PUT(self, **kwargs):
        pass

    def DELETE(self, img_id):
        pass


if __name__ == '__main__':
    SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(RootController(), '/', {'/': {'tools.db.on': True}})
    cherrypy.tree.mount(CategoryAPI(), '/api/category')
    #cherrypy.engine.subscribe('start_thread', ConnectDB)
    cherrypy.engine.start()
    cherrypy.engine.block()