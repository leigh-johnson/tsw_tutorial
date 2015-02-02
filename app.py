import os
import json
import pymysql
import cherrypy
from models import Base, Article, Category, Img, Admin, Jsonify
from cherrypy.process import wspbus, plugins


### Mako Templates ###
from mako.template import Template
from mako.lookup import TemplateLookup
#import mako.runtime
#mako.runtime.UNDEFINED = ''

path = os.path.abspath(os.path.dirname(__file__))
lookup = TemplateLookup(directories=[os.path.join(os.path.abspath(os.curdir)+'/view')], output_encoding='utf-8',collection_size=500)

### Plugins/Tools ###

from sqlalchemy import create_engine, update
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
def get_children(a_dir):
    return [name for name in os.listdir(a_dir)
        if os.path.isdir(os.path.join(a_dir, name))]

### App Index/Home/Root ### 

class RootController(object):

    @cherrypy.expose
    def index(self):
        character = {
            'name': "Nuwen", #cherrypy.request.headers.get('X-Tsw-Charactername')
            'faction': "Dragon", #cherrypy.request.headers.get('X-Tsw-Faction')
            'language': "_en" # cherrypy.request.headers.get('X-Tsw-Language')
        }

        result = Category.list(cherrypy.request.db)
        template = lookup.get_template(("/index"+character['language']+".html"))
        return template.render(categories=result, character=character, layout='default')

    @cherrypy.expose
    def category(self, category_id):
        character = {
            'name': "Nuwen", #cherrypy.request.headers.get('X-Tsw-Charactername')
            'faction': "Dragon", #cherrypy.request.headers.get('X-Tsw-Faction')
            'language': "_en" # cherrypy.request.headers.get('X-Tsw-Language')
        }

        pass

    @cherrypy.expose
    def article(self, article_id='None'):
        character = {
            'name': "Nuwen", #cherrypy.request.headers.get('X-Tsw-Charactername')
            'faction': "Dragon", #cherrypy.request.headers.get('X-Tsw-Faction')
            'language': "_en" # cherrypy.request.headers.get('X-Tsw-Language')
        }
        categories = Category.list(cherrypy.request.db)
        template = lookup.get_template(("/index"+character['language']+".html"))
        if article_id == 'None':
            return template.render(categories=categories, character=character, layout='default')

        article = cherrypy.request.db.query(Article).filter(Article.id == article_id).one()
        return template.render(categories=categories, character=character, layout=article.layout, article=article)




    @cherrypy.expose
    def login(self):
        pass

    ## UNIT TEST DATA ##
    @cherrypy.expose
    def build_data(self):
        img_1 = Img(
            src='http://placehold.it/350x200',
            title='Placeholder img 1')
        img_2 = Img(
            src='http://placehold.it/350x200',
            title='Placeholder img 2')
        img_3 = Img(
            src='http://placehold.it/350x200',
            title='Placeholder img 3')
        article_1 = Article(
            title_en='Hero image',
            description_en='Hero image description',
            body_en="Layout: hero image. A single hero image with a short caption",
            priority=30,
            layout='image-hero',
            )
        article_2 = Article(
            title_en='Image asides',
            description_en='How to move',
            body_en="Layout: image asides",
            priority=20,
            layout='image-aside',
            )
        article_3 = Article(
            title_en='Movement',
            description_en='How to move',
            body_en="Zombie ipsum brains reversus ab cerebellum viral inferno, brein nam rick mend grimes malum cerveau cerebro.",
            priority=10,
            layout='section-aside',
            )
        category_1 = Category(
            title_en="Image layouts",
            description_en="Layouts with images",
            body_en="Category description. Zombie ipsum brains reversus ab cerebellum viral inferno, brein nam rick mend grimes malum cerveau cerebro.",
            priority=10,
            )
        category_2 = Category(
            title_en="Social & Friendship",
            description_en="How to make friends",
            body_en="Zombie ipsum brains reversus ab cerebellum viral inferno, brein nam rick mend grimes malum cerveau cerebro.",
            priority=20,
            )
        category_3 = Category(
            title_en="Dungeons",
            description_en="How to dungeon",
            body_en="Zombie ipsum brains reversus ab cerebellum viral inferno, brein nam rick mend grimes malum cerveau cerebro.",
            priority=30,
            )   
        article_1.imgs.append(img_1)
        article_1.imgs.append(img_2)
        article_1.imgs.append(img_3)
        article_2.imgs.append(img_1)
        article_2.imgs.append(img_2)
        category_1.articles.append(article_1)
        category_1.articles.append(article_2)
        category_1.articles.append(article_3)
        category_2.articles.append(article_3)
        category_3.articles.append(article_2)
        category_1.imgs.append(img_1)
        category_2.imgs.append(img_2)
        category_3.imgs.append(img_3)

        result = cherrypy.request.db.add_all([article_1, article_2, article_3, category_1, category_2, category_3, img_1, img_2, img_3])
        return result


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

    def PUT(self, category_id, **kwargs):
        '''
        If authorized, persist .update() on session
        **KWARGS:
        key=value
        No validation strategy implemented, use with caution
        '''
        result = cherrypy.request.db.query(Category).filter(Category.id == category_id).update(kwargs)
        return json.dumps(result, cls=Jsonify)

    def DELETE(self, category_id):
        '''
        Marks object for delete in session
        '''
        result = cherrypy.request.db.query(Category).filter(Category.id == category_id).delete()
        return json.dumps(result, cls=Jsonify)


class ArticleAPI(object):

    exposed = True

    def GET(self, article_id=None):
        '''
        Returns article_id if id is supplied OR
        all article records if no id is supplied
        '''
        if article_id == None:
            result = Article.list(cherrypy.request.db)
            return json.dumps(result, cls=Jsonify)
        elif cherrypy.request.db.query(Article).get(article_id):
            result = cherrypy.request.db.query(Article).get(article_id)
            return json.dumps(result, cls=Jsonify)
        return 'Article ID not found.'

    def POST(self, **kwargs):
        '''
        If authorized, persist a new Article() to session and return it
        No validation strategy implemented, use with caution
        '''
        result = Article()
        cherrypy.request.db.add(result)
        return json.dumps(result, cls=Jsonify)

    def PUT(self, article_id, **kwargs):
        '''
        If authorized, persist .update() on session
        **KWARGS:
        key=value
        No validation strategy implemented, use with caution
        '''
        result = cherrypy.request.db.query(Article).filter(Article.id == article_id).update(kwargs)
        return json.dumps(result, cls=Jsonify)

    def DELETE(self, article_id):
        '''
        Marks object for delete in session
        '''
        result = cherrypy.request.db.query(Article).filter(Article.id == article_id).delete()
        return json.dumps(result, cls=Jsonify)



class ImgAPI(object):

    exposed = True

    def GET(self, img_id=None):
        '''
        Returns img_id if id is supplied OR
        all img records if no id is supplied
        '''
        if img_id == None:
            result = Img.list(cherrypy.request.db)
            return json.dumps(result, cls=Jsonify)
        elif cherrypy.request.db.query(Img).get(img_id):
            result = cherrypy.request.db.query(Img).get(img_id)
            return json.dumps(result, cls=Jsonify)
        return 'Img ID not found.'

    def POST(self, **kwargs):
        '''
        If authorized, persist a new Img() to session and return it
        No validation strategy implemented, use with caution
        '''
        result = Img()
        cherrypy.request.db.add(result)
        return json.dumps(result, cls=Jsonify)

    def PUT(self, img_id, **kwargs):
        '''
        If authorized, persist .update() on session
        **KWARGS:
        key=value
        No validation strategy implemented, use with caution
        '''
        result = cherrypy.request.db.query(Img).filter(Img.id == img_id).update(kwargs)
        return json.dumps(result, cls=Jsonify)

    def DELETE(self, img_id):
        '''
        Marks object for delete in session
        '''
        result = cherrypy.request.db.query(Img).filter(Img.id == img_id).delete()
        return json.dumps(result, cls=Jsonify)

### Config ###

##cherrypy.config.update('app.conf')

if __name__ == '__main__':
    cherrypy.config.update('config/app.conf')
    SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(RootController(), '/', config='config/app.conf')
    cherrypy.tree.mount(CategoryAPI(), '/api/category', config='config/api.conf')
    cherrypy.tree.mount(Img(), '/api/img', config='config/api.conf')
    cherrypy.tree.mount(ArticleAPI(), '/api/article', config='config/api.conf')

    #cherrypy.engine.subscribe('start_thread', ConnectDB)
cherrypy.engine.start()
cherrypy.engine.block()