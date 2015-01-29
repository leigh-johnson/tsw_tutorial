import os, os.path
import json
import pymysql
import cherrypy
from models import Base, Article, Category, Img, Admin, Jsonify
from cherrypy.process import wspbus, plugins


### Mako Templates ###
from mako.template import Template
from mako.lookup import TemplateLookup

lookup = TemplateLookup(directories=["view"])

### Plugins/Tools ###

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


### App Index/Home/Root ### 

class RootController(object):

    @cherrypy.expose
    
    def index(self):
        # Localization thread variable
        # Return tutorial categories, progress indicator, faction stylesheets
        categories = [category for category in Category.list(cherrypy.request.db)]
        template = lookup.get_template("index.html")
        return template.render(categories=categories, layout='default')

    @cherrypy.expose
    def category(self):
        pass

    @cherrypy.expose
    def article(self):
        pass

    @cherrypy.expose
    def login(self):
        pass


### RESTful API Controllers ###
### ALL RETURNS ON API ROUTES AGONOSTICALLY RETURN `result` ###

class CategoryAPI(object):

    exposed = True

    def GET(self, category_id=None):
        '''
        Returns category_id if id is supplied OR
        all category records if no id is supplied
        '''
        if category_id == None:
            result = Category.list(cherrypy.request.db)
            return json.dumps(result, cls=Jsonify)
        elif cherrypy.request.db.query(Category).get(category_id):
            result = cherrypy.request.db.query(Category).get(category_id)
            return json.dumps(result, cls=Jsonify)
        return 'Category ID not found.'

    def POST(self, **kwargs):
        '''
        If authorized, persist a new Category() to session and return it
        No validation strategy implemented, use with caution
        '''
        result = Category()
        cherrypy.request.db.add(result)
        return json.dumps(result, cls=Jsonify)

    def PUT(self, **kwargs):
        '''
        If authorized, persist .update() on session
        **KWARGS:
        key=value
        No validation strategy implemented, use with caution
        '''
        result = cherrypy.request.db.query(Category).filter(id == category_id).update(kwargs)
        cherrypy.request.db.add(result)
        return json.dumps(result, cls=Jsonify)

    def DELETE(self, category_id):
        '''
        Marks object for delete in session
        '''
        result = cherrypy.request.db.query(Category).filter(id == category_id)
        cherrypy.request.db.delete(result)
        return result


class ArticleAPI(object): 
    exposed = True

    def GET(self, article_id=None):
        '''
        Returns article_id if id is supplied OR
        all article records if no id is supplied
        '''
        if article_id == None:
            result = [article for article in Article.list(cherrypy.request.db)]
            return result
        else: 
            result = cherrypy.request.db.query(Article).get(article_id)
            return result

    def POST(self, **kwargs):
        '''If authorized, persist a new Article() to session and return it
        No validation strategy implemented, use with caution
        '''
        result = Article(**kwargs)
        cherrypy.request.db.add(result)
        return result

    def PUT(self, **kwargs):
        '''If authorized, persist .update() on session
        **KWARGS:
        key=value
        No validation strategy implemented, use with caution
        '''
        #if authorized
        values = {}
        for key, value in kwargs.iteritems():
            values[key] = value
        article_id = values[article_id]
        result = cherrypy.request.db.query(Article).filter(id == article_id).update(values)
        return result

    def DELETE(self, article_id):
        '''Marks object for delete in session
        Cascade should NEVER be handled in the Controllers
        Instead, declaratively state cascadence in model parameters'''
        result = cherrypy.request.db.query(Article).filter(id == article_id).delete()
        return result

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

### Config ###

cherrypy.config.update('app.conf')

if __name__ == '__main__':
    cherrypy.config.update('app.conf')
    SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(RootController(), '/', config='app.conf')
    cherrypy.tree.mount(CategoryAPI(), '/api/category', config='api.conf')
    cherrypy.tree.mount(Img(), '/api/img', config='api.conf')
    cherrypy.tree.mount(ArticleAPI(), '/api/article', config='api.conf')

    #cherrypy.engine.subscribe('start_thread', ConnectDB)
cherrypy.engine.start()
cherrypy.engine.block()