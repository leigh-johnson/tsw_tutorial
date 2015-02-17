## -*- coding: utf-8 -*-
import os
import json
import MySQLdb
import cherrypy
from auth import AuthController, require, check_auth
from api import ArticleAPI
from models import Base, Article, Body_en, Body_fr, Body_de, Admin, Jsonify
from sqlalchemy.ext.serializer import loads, dumps
from sqlalchemy.exc import IntegrityError
from cherrypy.process import wspbus, plugins


### Mako Templates ###
from mako.template import Template
from mako.lookup import TemplateLookup
#import mako.runtime
#mako.runtime.UNDEFINED = ''

path = os.path.abspath(os.path.dirname(__file__))
lookup = TemplateLookup(directories=[os.path.join(os.path.abspath(os.curdir)+'/view')], output_encoding='utf-8',collection_size=500, strict_undefined=True)

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

        categories = Article.list(cherrypy.request.db)
        template = lookup.get_template(("client/index.html"))
        return template.render(categories=categories, character=character, lang=character['language'])

    @cherrypy.expose
    def article(self, _id=None):
        character = {
            'name': "Nuwen", #cherrypy.request.headers.get('X-Tsw-Charactername')
            'faction': "Dragon", #cherrypy.request.headers.get('X-Tsw-Faction')
            'language': "en" # cherrypy.request.headers.get('X-Tsw-Language')
        }
        if _id == None:
            raise cherrypy.HTTPRedirect('/')
        categories = Article.list(cherrypy.request.db)
        article = cherrypy.request.db.query(Article).filter(Article._id == _id).one()
        template = lookup.get_template("client/index.html")
        return template.render(categories=categories, article=article, character=character, lang=character['language'])

    @cherrypy.expose
    def build_data(self):
        body_1 = Body_en(
            text='<figure><img alt="" src="http://placehold.it/200x200/1e1e1e/ffffff/&amp;text=200x200px" style="float: left;" /><figcaption><p><span style="font-family: Oxygen, sans-serif; font-size: 18px; font-style: normal; font-variant: normal; line-height: 27px; background-color: rgb(252, 254, 255);">Changchunsaurus Gyposaurus Rinconsaurus Aggiosaurus Scelidosaurus Dryosaurus Anatosaurus Astrodon Asiamericana Ignavusaurus Gongxianosaurus Rebbachisaurus Zhuchengosaurus Trinisaura Kritosaurus Cryptovolans Erliansaurus Deltadromeus Jiangshanosaurus Hongshanosaurus Protognathosaurus Stegopelta Symphyrophus Echinodon Rahiolisaurus. </span></p></figcaption></figure>'
            )
        body_2 = Body_en(
            text='<figure><img alt="" src="http://placehold.it/200x200/1e1e1e/ffffff/&amp;text=200x200px" style="float: left;" /><figcaption><p><span style="font-family: Oxygen, sans-serif; font-size: 18px; font-style: normal; font-variant: normal; line-height: 27px; background-color: rgb(252, 254, 255);">Changchunsaurus Gyposaurus Rinconsaurus Aggiosaurus Scelidosaurus Dryosaurus Anatosaurus Astrodon Asiamericana Ignavusaurus Gongxianosaurus Rebbachisaurus Zhuchengosaurus Trinisaura Kritosaurus Cryptovolans Erliansaurus Deltadromeus Jiangshanosaurus Hongshanosaurus Protognathosaurus Stegopelta Symphyrophus Echinodon Rahiolisaurus. </span></p></figcaption></figure>'
            )
        body_3 = Body_en(
            text='<figure><img alt="" src="http://placehold.it/200x200/1e1e1e/ffffff/&amp;text=200x200px" style="float: left;" /><figcaption><p><span style="font-family: Oxygen, sans-serif; font-size: 18px; font-style: normal; font-variant: normal; line-height: 27px; background-color: rgb(252, 254, 255);">Changchunsaurus Gyposaurus Rinconsaurus Aggiosaurus Scelidosaurus Dryosaurus Anatosaurus Astrodon Asiamericana Ignavusaurus Gongxianosaurus Rebbachisaurus Zhuchengosaurus Trinisaura Kritosaurus Cryptovolans Erliansaurus Deltadromeus Jiangshanosaurus Hongshanosaurus Protognathosaurus Stegopelta Symphyrophus Echinodon Rahiolisaurus. </span></p></figcaption></figure>'
            )
        body_4 = Body_en(
            text='<figure><img alt="" src="http://placehold.it/200x200/1e1e1e/ffffff/&amp;text=200x200px" style="float: left;" /><figcaption><p><span style="font-family: Oxygen, sans-serif; font-size: 18px; font-style: normal; font-variant: normal; line-height: 27px; background-color: rgb(252, 254, 255);">Changchunsaurus Gyposaurus Rinconsaurus Aggiosaurus Scelidosaurus Dryosaurus Anatosaurus Astrodon Asiamericana Ignavusaurus Gongxianosaurus Rebbachisaurus Zhuchengosaurus Trinisaura Kritosaurus Cryptovolans Erliansaurus Deltadromeus Jiangshanosaurus Hongshanosaurus Protognathosaurus Stegopelta Symphyrophus Echinodon Rahiolisaurus. </span></p></figcaption></figure>'
            )
        body_5 = Body_en(
            text='<figure><img alt="" src="http://placehold.it/200x200/1e1e1e/ffffff/&amp;text=200x200px" style="float: left;" /><figcaption><p><span style="font-family: Oxygen, sans-serif; font-size: 18px; font-style: normal; font-variant: normal; line-height: 27px; background-color: rgb(252, 254, 255);">Changchunsaurus Gyposaurus Rinconsaurus Aggiosaurus Scelidosaurus Dryosaurus Anatosaurus Astrodon Asiamericana Ignavusaurus Gongxianosaurus Rebbachisaurus Zhuchengosaurus Trinisaura Kritosaurus Cryptovolans Erliansaurus Deltadromeus Jiangshanosaurus Hongshanosaurus Protognathosaurus Stegopelta Symphyrophus Echinodon Rahiolisaurus. </span></p></figcaption></figure>'
            )
        body_6 = Body_en(
            text='<figure><img alt="" src="http://placehold.it/200x200/1e1e1e/ffffff/&amp;text=200x200px" style="float: left;" /><figcaption><p><span style="font-family: Oxygen, sans-serif; font-size: 18px; font-style: normal; font-variant: normal; line-height: 27px; background-color: rgb(252, 254, 255);">Changchunsaurus Gyposaurus Rinconsaurus Aggiosaurus Scelidosaurus Dryosaurus Anatosaurus Astrodon Asiamericana Ignavusaurus Gongxianosaurus Rebbachisaurus Zhuchengosaurus Trinisaura Kritosaurus Cryptovolans Erliansaurus Deltadromeus Jiangshanosaurus Hongshanosaurus Protognathosaurus Stegopelta Symphyrophus Echinodon Rahiolisaurus. </span></p></figcaption></figure>'
            )     
        body_7 = Body_en(
            text='<figure><img alt="" src="http://placehold.it/200x200/1e1e1e/ffffff/&amp;text=200x200px" style="float: left;" /><figcaption><p><span style="font-family: Oxygen, sans-serif; font-size: 18px; font-style: normal; font-variant: normal; line-height: 27px; background-color: rgb(252, 254, 255);">Changchunsaurus Gyposaurus Rinconsaurus Aggiosaurus Scelidosaurus Dryosaurus Anatosaurus Astrodon Asiamericana Ignavusaurus Gongxianosaurus Rebbachisaurus Zhuchengosaurus Trinisaura Kritosaurus Cryptovolans Erliansaurus Deltadromeus Jiangshanosaurus Hongshanosaurus Protognathosaurus Stegopelta Symphyrophus Echinodon Rahiolisaurus. </span></p></figcaption></figure>'
            )
        body_8 = Body_en(
            text='<figure><img alt="" src="http://placehold.it/200x200/1e1e1e/ffffff/&amp;text=200x200px" style="float: left;" /><figcaption><p><span style="font-family: Oxygen, sans-serif; font-size: 18px; font-style: normal; font-variant: normal; line-height: 27px; background-color: rgb(252, 254, 255);">Changchunsaurus Gyposaurus Rinconsaurus Aggiosaurus Scelidosaurus Dryosaurus Anatosaurus Astrodon Asiamericana Ignavusaurus Gongxianosaurus Rebbachisaurus Zhuchengosaurus Trinisaura Kritosaurus Cryptovolans Erliansaurus Deltadromeus Jiangshanosaurus Hongshanosaurus Protognathosaurus Stegopelta Symphyrophus Echinodon Rahiolisaurus. </span></p></figcaption></figure>'
            )
        body_9 = Body_en(
            text='<figure><img alt="" src="http://placehold.it/200x200/1e1e1e/ffffff/&amp;text=200x200px" style="float: left;" /><figcaption><p><span style="font-family: Oxygen, sans-serif; font-size: 18px; font-style: normal; font-variant: normal; line-height: 27px; background-color: rgb(252, 254, 255);">Changchunsaurus Gyposaurus Rinconsaurus Aggiosaurus Scelidosaurus Dryosaurus Anatosaurus Astrodon Asiamericana Ignavusaurus Gongxianosaurus Rebbachisaurus Zhuchengosaurus Trinisaura Kritosaurus Cryptovolans Erliansaurus Deltadromeus Jiangshanosaurus Hongshanosaurus Protognathosaurus Stegopelta Symphyrophus Echinodon Rahiolisaurus. </span></p></figcaption></figure>'
            )
        article_1 = Article(
            title_en='Category of Things',
            order=30,
            layout='default',
            public= True,
            is_category=True
            )
        article_2 = Article(
            title_en='English text/img thing',
            order=20,
            public=True
            )
        article_3 = Article(
            title_en='English video thing',
            order=10,
            layout='video',
            public=True
            )
        article_4 = Article(
            title_en='Orphan article qq',
            order=30,
            layout='default',
            public=False)
        article_5 = Article(
            title_en="Sub-category of things",
            order=10,
            public=True,
            is_category=True)
        article_6 = Article(
            title_en="Article in a subcategory",
            order=10,
            public=True)
        article_1.body_en.append(body_1)
        article_1.body_en.append(body_2)
        article_1.body_en.append(body_3)
        article_2.body_en.append(body_4)
        article_2.body_en.append(body_5)
        article_2.body_en.append(body_6)
        article_3.body_en.append(body_7)


        article_6.body_en.append(body_8)
        article_6.body_en.append(body_9)

        article_1.articles.append(article_2)
        article_1.articles.append(article_3)
        article_1.articles.append(article_5)
        article_5.articles.append(article_6)

        result = cherrypy.request.db.add_all([article_1, article_2, article_3, article_4, article_5, article_6])
        return result



class AdminController(object):
    @cherrypy.expose
    def index(self, lang='en'):
        cookie = cherrypy.request.cookie
        if 'lang' in cookie.keys():
            lang = cookie['lang'].value
        categories = Article.list(cherrypy.request.db)
        template = lookup.get_template(('admin/index.html'))
        return template.render(categories=categories, lang=lang)

    @cherrypy.expose
    def article(self, _id=None, lang='en'):
        # req lang changes
        cookie = cherrypy.request.cookie
        if 'lang' in cookie.keys():
            lang = cookie['lang'].value
        categories = Article.list(cherrypy.request.db)
        article = cherrypy.request.db.query(Article).filter(Article._id == _id).one()
        template = lookup.get_template('admin/layouts/'+article.layout+'.html')
        return template.render(categories=categories, article=article, lang=lang)

    @cherrypy.expose
    def new(self, lang='en'):
        '''Serve new article template'''
        cookie = cherrypy.request.cookie
        if 'lang' in cookie.keys():
            lang = cookie['lang'].value
        categories = Article.list(cherrypy.request.db)
        template = lookup.get_template('admin/new.html')
        return template.render(categories=categories, lang=lang)
        
    @cherrypy.expose
    def setLang(self, lang):
        # Set cookie to send
        path = cherrypy.request.path_info
        cookie = cherrypy.response.cookie

        cookie['lang'] = lang
        cookie['lang']['path'] = 'admin'
        cookie['lang']['max-age'] = 3600
        return json.dumps({'responseText':"Language set!"})

    @cherrypy.expose
    def assign(self, p_id, c_id):
        '''Removes a child Article() from parent, assigns to new parent'''
        new_parent = cherrypy.request.db.query(Article).filter(Article._id == p_id).one()
        child = cherrypy.request.db.query(Article).filter(Article._id == c_id).one()
        old_parent = cherrypy.request.db.query(Article).filter(Article._id == child.parent_id).one()
        old_parent.articles.remove(child)
        new_parent.articles.append(child)
        return json.dumps({'responseText': "Category assigned"})

    @cherrypy.expose
    def setLayout(self, _id, layout):
        '''Sets the layout of an Article() instance'''
        article = cherrypy.request.db.query(Article).get(_id)
        article.layout = layout
        return json.dumps({'responseText': "Layout changed to %s" %layout})

    @cherrypy.expose
    def setIsCategory(self, _id, is_category):
        '''Sets the is_category bool of an Article() instance'''
        article = cherrypy.request.db.query(Article).get(_id)
        article.is_category = is_category
        return json.dumps({'responseText' : "is_category bool set to %s" % is_category})

    @cherrypy.expose
    def setIsPublic(self, _id, is_public):
        '''Sets the is_public bool of an Article() instance'''
        article = cherrypy.request.db.query(Article).get(_id)
        article.public = is_public
        return json.dumps({'responseText' : "is_public bool set to %s" % is_public})


class APIController(object):
    exposed = True
    article = ArticleAPI()
    ## Any other APIs can share this mount point

### Config ###

if __name__ == '__main__':
    cherrypy.config.update('config/app.conf')
    SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(ClientController(), '/', config='config/app.conf')
    cherrypy.tree.mount(APIController(), '/admin/api', config='config/api.conf')
    cherrypy.tree.mount(AdminController(), '/admin')

cherrypy.engine.start()
cherrypy.engine.block()