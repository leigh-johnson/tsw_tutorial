import os, os.path
import pymysql
import json
import cherrypy
from models import Base, Article, Category, Img, Admin
from cherrypy.process import wspbus, plugins


### Mako Templates ###
from mako.template import Template
from mako.lookup import TemplateLookup

lookup = TemplateLookup(directories=["templates"])

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

class RootController(object):

    @cherrypy.expose
    @jsonify
    def index(self):
        # Localization thread variable
        # Return tutorial categories, progress indicator, faction stylesheets
        categories = [category for category in Category.list(cherrypy.request.db)]
        template = lookup.get_template("index.html")
        return template.render(categories=categories)

class CategoryController(object):

    exposed = True
    def GET(self, id=None):
        '''
        Returns category_id if id is supplied
        Or a list of category records if no id is supplied
        '''
        pass

    @jsonify
    def POST(self, **kwargs):
        category = Category(**kwargs)
        cherrypy.request.db.add(category)
        template = lookup.get_template("index.html")
        return template.render(categories=category)



if __name__ == '__main__':
    SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(RootController(), '/', {'/': {'tools.db.on': True}})
    cherrypy.tree.mount(CategoryController(), '/category')
    #cherrypy.engine.subscribe('start_thread', ConnectDB)
    cherrypy.engine.start()
    cherrypy.engine.block()