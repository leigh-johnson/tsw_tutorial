## -*- coding: utf-8 -*-
import os
import json
import MySQLdb
import cherrypy
from admin import AdminController
from auth import AuthController, require, check_auth
from api import CategoryAPI, ArticleAPI, ImgAPI
from models import Base, Article, Category, Body, Img, Admin, Jsonify
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
        db_path = 'root:normacreedlives@127.0.0.1/tsw_tuts'
        #db_path = os.path.abspath(os.path.join(os.curdir, 'data/my.db'))
        self.sa_engine = create_engine('mysql+mysqldb://%s?charset=utf8' % db_path, echo=True)
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

### Client/Tutorial Controller ### 
class ClientController(object):
    '''Tutorial client. Views in views/client/_locale'''
    @cherrypy.expose
    def index(self):
        character = {
            'name': "Nuwen", #cherrypy.request.headers.get('X-Tsw-Charactername')
            'faction': "Dragon", #cherrypy.request.headers.get('X-Tsw-Faction')
            'language': "en" # cherrypy.request.headers.get('X-Tsw-Language')
        }

        categories = Category.list(cherrypy.request.db)
        template = lookup.get_template(("client/index.html"))
        return template.render(categories=categories, character=character, layout='default', lang=character['language'])

    @cherrypy.expose
    def category(self, category_id=None):
        character = {
            'name': "Nuwen", #cherrypy.request.headers.get('X-Tsw-Charactername')
            'faction': "Dragon", #cherrypy.request.headers.get('X-Tsw-Faction')
            'language': "en" # cherrypy.request.headers.get('X-Tsw-Language')
        }
        if category_id == None:
            raise cherrypy.HTTPRedirect('/')
        categories = Category.list(cherrypy.request.db)
        category = cherrypy.request.db.query(Category).filter(Category.id == category_id).one()
        template = lookup.get_template("layouts/"+category.layout+".html")
        return template.render(categories=categories, category=category, character=character, lang=character['language'])

    @cherrypy.expose
    def article(self, article_id='None'):
        character = {
            'name': "Nuwen", #cherrypy.request.headers.get('X-Tsw-Charactername')
            'faction': "Dragon", #cherrypy.request.headers.get('X-Tsw-Faction')
            'language': "en" # cherrypy.request.headers.get('X-Tsw-Language')
        }
        categories = Category.list(cherrypy.request.db)
        template = lookup.get_template(("client/index"+character['language']+".html"))
        if article_id == 'None':
            return template.render(categories=categories, character=character, layout='default')

        article = cherrypy.request.db.query(Article).filter(Article.id == article_id).one()
        return template.render(categories=categories, character=character, layout=article.layout, article=article)
   ## UNIT TEST DATA ##
      ## UNIT TEST DATA ##
    @cherrypy.expose
    def build_data(self):

        body_1 = Body(
            text="Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec qu"
            )
        body_2 = Body(
            text="Es gibt im Moment in diese Mannschaft, oh, einige Spieler vergessen ihnen Profi was sie sind. Ich lese nicht sehr viele Zeitungen, aber ich habe gehört viele Situationen. Erstens: wir haben nicht offe"
            )
        body_3 = Body(
            text="En se réveillant un matin après des rêves agités, Gregor Samsa se retrouva, dans son lit, métamorphosé en un monstrueux insecte. Il était sur le dos, un dos aussi dur qu’une carapace, et, en relevant."
            )
        body_4 = Body(
            text="En se réveillant un matin après des rêves agités, Gregor Samsa se retrouva, dans son lit, métamorphosé en un monstrueux insecte. Il était sur le dos, un dos aussi dur qu’une carapace, et, en relevant."
            )
        body_5 = Body(
            text="En se réveillant un matin après des rêves agités, Gregor Samsa se retrouva, dans son lit, métamorphosé en un monstrueux insecte. Il était sur le dos, un dos aussi dur qu’une carapace, et, en relevant."
            )
        body_6 = Body(
            text="En se réveillant un matin après des rêves agités, Gregor Samsa se retrouva, dans son lit, métamorphosé en un monstrueux insecte. Il était sur le dos, un dos aussi dur qu’une carapace, et, en relevant."
            )     
        body_7 = Body(
            text="En se réveillant un matin après des rêves agités, Gregor Samsa se retrouva, dans son lit, métamorphosé en un monstrueux insecte. Il était sur le dos, un dos aussi dur qu’une carapace, et, en relevant."
            )
        body_8 = Body(
            text="En se réveillant un matin après des rêves agités, Gregor Samsa se retrouva, dans son lit, métamorphosé en un monstrueux insecte. Il était sur le dos, un dos aussi dur qu’une carapace, et, en relevant."
            )
        body_9 = Body(
            text="En se réveillant un matin après des rêves agités, Gregor Samsa se retrouva, dans son lit, métamorphosé en un monstrueux insecte. Il était sur le dos, un dos aussi dur qu’une carapace, et, en relevant."
            )  
        img_1 = Img(
            src='http://placehold.it/350x200&text=img_1',
            title='Placeholder img 1')
        img_2 = Img(
            src='http://placehold.it/350x200&text=img_2',
            title='Placeholder img 2')
        img_3 = Img(
            src='http://placehold.it/350x200&text=img_3',
            title='Placeholder img 3')
        article_1 = Article(
            title_en='Hero image',
            description_en='Hero image description',
            order=30,
            layout='image-hero',
            )
        article_2 = Article(
            title_en='Image asides',
            description_en='How to move',
            order=20,
            layout='image-aside',
            )
        article_3 = Article(
            title_en='Full-width video',
            description_en='Full-width video',
            order=10,
            layout='video',
            )
        category_1 = Category(
            title_en="Default category layout",
            description_en="A section-aside style layout. Default display option for all categories.",
            order=10,
            )
        category_2 = Category(
            title_en="Video layouts",
            description_en="How to make friends",
            order=20,
            )
        category_3 = Category(
            title_en="Dungeons",
            description_en="How to dungeon",
            order=30,
            )   
        article_1.imgs.append(img_1)
        article_2.imgs.append(img_2)


        article_2.imgs.append(img_3)

        article_1.body_en.append(body_1)
        article_1.body_fr.append(body_2)
        article_1.body_de.append(body_3)

        article_2.body_en.append(body_4)
        article_2.body_fr.append(body_5)
        article_2.body_de.append(body_6)

        article_3.body_en.append(body_7)
        article_3.body_fr.append(body_8)
        article_3.body_de.append(body_9)

        category_1.body_en.append(body_1)
        #category_1.body_fr.append(body_2)
        #category_1.body_de.append(body_3)

        category_2.body_en.append(body_4)
        #category_2.body_fr.append(body_5)
        #category_2.body_de.append(body_6)

        category_3.body_en.append(body_7)
        #category_3.body_fr.append(body_8)
        #category_3.body_de.append(body_9)

        category_1.articles.append(article_1)
        category_1.articles.append(article_2)
        category_2.articles.append(article_3)
        category_1.imgs.append(img_1)
        category_2.imgs.append(img_2)
        category_3.imgs.append(img_3)

        result = cherrypy.request.db.add_all([article_1, article_2, article_3, category_1, category_2, category_3, img_1, img_2, img_3])
        return result
class AdminController(object):
    @cherrypy.expose
    def index(self, lang='en'):
        cookie = cherrypy.request.cookie
        if 'lang' in cookie.keys():
            lang = cookie['lang'].value
        categories = Category.list(cherrypy.request.db)
        template = lookup.get_template(('admin/index.html'))
        return template.render(categories=categories, lang=lang)

    @cherrypy.expose
    def category(self, category_id=None, lang='en'):
        # req lang changes
        cookie = cherrypy.request.cookie
        if 'lang' in cookie.keys():
            lang = cookie['lang'].value
        elif category_id == None:
            raise cherrypy.HTTPRedirect('/')
        categories = Category.list(cherrypy.request.db)
        category = cherrypy.request.db.query(Category).filter(Category.id == category_id).one()
        template = lookup.get_template('admin/layouts/'+category.layout+'.html')
        return template.render(categories=categories, category=category, lang=lang)

    @cherrypy.expose
    def article(self):
        pass

    @cherrypy.expose
    def new(self, doc_type=None):
        if doc_type==None:
            raise cherrypy.HTTPRedirect('/')
        categories = Category.list(cherrypy.request.db)
        template = lookup.get_template('admin/partials/new.html')
        return template.render(categories=categories, doc_type=doc_type)

    @cherrypy.expose
    def edit(self, doc_type=None, _id=None, lang="en"):
        categories = Category.list(cherrypy.request.db)
        template = lookup.get_template('admin/edit.html')
        return template.render(categories=categories, doc_type=doc_type, _id=_id, lang=lang)
    
    @cherrypy.expose
    def setLang(self, lang):
        # Set cookie to send
        cookie = cherrypy.response.cookie

        cookie['lang'] = lang
        cookie['lang']['path'] = 'admin'
        cookie['lang']['max-age'] = 3600

        raise cherrypy.HTTPRedirect('/')

    #category.new = new(type='category')
    #category.edit = edit(_type='category')
    #article.new = new(type='article')
    #article.edit = edit(_type='article')

class APIController(object):
    exposed = True
    category = CategoryAPI()
    article = ArticleAPI()

### Config ###

if __name__ == '__main__':
    cherrypy.config.update('config/app.conf')
    SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(ClientController(), '/', config='config/app.conf')
    cherrypy.tree.mount(APIController(), '/api', config='config/api.conf')
    cherrypy.tree.mount(AdminController(), '/admin')

cherrypy.engine.start()
cherrypy.engine.block()