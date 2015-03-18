## -*- coding: utf-8 -*-
import os
import json
import MySQLdb
import cherrypy
import re
import csv
from collections import OrderedDict
from auth import AuthController, require, check_auth
from api import ArticleAPI, TagAPI
from models import Base, Article, Body_en, Body_fr, Body_de, Admin, Tag, Jsonify
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.serializer import loads, dumps
from sqlalchemy.exc import IntegrityError
from cherrypy.process import wspbus, plugins
from cherrypy.process.plugins import Daemonizer


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
        db_conn = cherrypy.config.get("db.connection")
        #db_path = os.path.abspath(os.path.join(os.curdir, 'data/my.db'))
        self.sa_engine = create_engine('mysql+mysqldb://%s?charset=utf8' % db_conn, echo=True)
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
        # @todo remove static data
        character = {
            'name': "Nuwen", #cherrypy.request.headers.get('X-Tsw-Charactername')
            'faction': "dragon", #cherrypy.request.headers.get('X-Tsw-Faction')
            'language': "en" # cherrypy.request.headers.get('X-Tsw-Language')
        }
        tags = Tag.list(cherrypy.request.db)
        categories = Article.list(cherrypy.request.db)
        template = lookup.get_template(('client/index.html'))
        return template.render(categories=categories, character=character, lang=character["language"], tags=tags)

    @cherrypy.expose
    def article(self, _id=None):
        # @todo remove static data
        character = {
            'name': "Nuwen", #cherrypy.request.headers.get('X-Tsw-Charactername')
            'faction': "Dragon", #cherrypy.request.headers.get('X-Tsw-Faction')
            'language': "en" # cherrypy.request.headers.get('X-Tsw-Language')
        }
        if _id == None:
            raise cherrypy.HTTPRedirect('/')
        categories = Article.list(cherrypy.request.db)
        article = cherrypy.request.db.query(Article).filter(Article._id == _id).one()
        tags = Tag.list(cherrypy.request.db)
        template = lookup.get_template('client/layouts/'+article.layout+'.html')
        return template.render(categories=categories, article=article, character=character, lang=character["language"], tags=tags)

    @cherrypy.expose
    def search(self, lang="en", tag=None, term=None, *args):
        '''Search function. Prioritizes article tags/keywords, then performs a fuzzy search'''
        # @todo remove static data
        character = {
            'name': "Nuwen", #cherrypy.request.headers.get('X-Tsw-Charactername')
            'faction': "Dragon", #cherrypy.request.headers.get('X-Tsw-Faction')
            'language': "en" # cherrypy.request.headers.get('X-Tsw-Language')
        }
        categories = Article.list(cherrypy.request.db)
        tags = Tag.list(cherrypy.request.db)
        template = lookup.get_template('client/layouts/search.html')

        # return tag results
        if tag != None:
            title = "title_"+lang
            result = cherrypy.request.db.query(Tag).filter((Tag.title_en == tag)|(Tag.title_fr == tag)|(Tag.title_de == tag)).one()
            query = "tag= "+tag
            return template.render(categories=categories, character=character, lang=character["language"], tags=tags, results=result, query=query)
        
        elif term != None:
        # return string-match to Body_$lang.text & Article.title_$lang
            bodies = {"body_de": Body_de, "body_en": Body_en, "body_fr": Body_fr}
            for k,v in bodies.iteritems():
                if k == "body_"+lang:
                    result = cherrypy.request.db.query(v, Article).join(Article).filter(
                    v.text.like('%' + term + '%')|(getattr(Article, "title_"+lang).like('%' + term + '%'))).all()
            query = "term= "+term
            return template.render(categories=categories, lang=lang, tags=tags, results=result, query=query)
        else:
            return "Could not interpret search, try again"

    @cherrypy.expose
    def help(self, lua_tag=None):
        '''Alias route to query articles by LUA tag'''
        categories = Article.list(cherrypy.request.db)
        tags = Tag.list(cherrypy.request.db)
        try:
            article = cherrypy.request.db.query(Article).filter(Article.lua_tag == lua_tag).one()
            template = lookup.get_template('client/layouts/'+article.layout+'.html')
            return template.render(categories=categories, article=article, character=character, lang=character["language"], tags=tags)
        except NoResultFound, e:
            raise cherrypy.HTTPRedirect('/')
        

class AdminController(object):
    @cherrypy.expose
    def index(self, lang='en'):
        cookie = cherrypy.request.cookie
        if 'lang' in cookie.keys():
            lang = cookie['lang'].value
        tags = Tag.list(cherrypy.request.db)
        categories = Article.list(cherrypy.request.db)
        template = lookup.get_template(('admin/index.html'))
        return template.render(categories=categories, lang=lang, tags=tags)

    @cherrypy.expose
    def article(self, _id=None, lang='en'):
        # req lang changes
        cookie = cherrypy.request.cookie
        if 'lang' in cookie.keys():
            lang = cookie['lang'].value
        categories = Article.list(cherrypy.request.db)
        article = cherrypy.request.db.query(Article).filter(Article._id == _id).one()
        tags = Tag.list(cherrypy.request.db)
        template = lookup.get_template('admin/layouts/'+article.layout+'.html')
        return template.render(categories=categories, article=article, lang=lang, tags=tags)

    @cherrypy.expose
    def new(self, **kwargs):
        '''Serve new article template'''
        article = Article()
        for k,v in kwargs.iteritems():
            setattr(article, k, v)
        cherrypy.request.db.add(article)
        cherrypy.request.db.flush()
        # flush to have access to ._id, otherwise None 
        raise cherrypy.HTTPRedirect('/admin/article?_id=%i' % article._id)

    @cherrypy.expose
    def tags(self, lang='en'):
        '''Serve a new tag template'''
        cookie = cherrypy.request.cookie
        if 'lang' in cookie.keys():
            lang = cookie['lang'].value
        categories = Article.list(cherrypy.request.db)
        tags = Tag.list(cherrypy.request.db)
        template = lookup.get_template('admin/new_tag.html')
        return template.render(categories=categories, lang=lang, tags=tags)

    @cherrypy.expose
    def search(self, lang="en", tag=None, term=None, *args):
        cookie = cherrypy.request.cookie
        if 'lang' in cookie.keys():
            lang = cookie['lang'].value
        categories = Article.list(cherrypy.request.db)
        tags = Tag.list(cherrypy.request.db)
        template = lookup.get_template('admin/layouts/search.html')

        # return tag results
        if tag != None:
            title = "title_"+lang
            result = cherrypy.request.db.query(Tag).filter((Tag.title_en == tag)|(Tag.title_fr == tag)|(Tag.title_de == tag)).one()
            query = "tag= "+tag
            return template.render(categories=categories, lang=lang, tags=tags, results=result, query=query)
        
        elif term != None:
        # return string-match to Body_$lang.text & Article.title_$lang
            bodies = {"body_de": Body_de, "body_en": Body_en, "body_fr": Body_fr}
            for k,v in bodies.iteritems():
                if k == "body_"+lang:
                    result = cherrypy.request.db.query(v, Article).join(Article).filter(
                    v.text.like('%' + term + '%')|(getattr(Article, "title_"+lang).like('%' + term + '%'))).all()
            query = "term= "+term
            return template.render(categories=categories, lang=lang, tags=tags, results=result, query=query)
        else:
            return "Could not interpret search, try again"


    @cherrypy.expose
    def setTag(self,_id=None, tag_id=None, remove=False):
        '''Creates or removes an association between Article() & Tag() instance'''
        if remove == 'True':
            article = cherrypy.request.db.query(Article).get(_id)
            tag = cherrypy.request.db.query(Tag).get(tag_id)
            article.tags.remove(tag)
        else:
            article = cherrypy.request.db.query(Article).get(_id)
            tag = cherrypy.request.db.query(Tag).get(tag_id)
            article.tags.append(tag)
        return json.dumps({'responseText': 'Updated tag: %s' %tag.title_en})

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
    def setParentId(self, p_id, c_id):
        '''Removes a child Article() from parent, assigns to new parent'''
        new_parent = cherrypy.request.db.query(Article).filter(Article._id == p_id).one()
        child = cherrypy.request.db.query(Article).filter(Article._id == c_id).one()
        if child.parent_id != None:
            old_parent = cherrypy.request.db.query(Article).filter(Article._id == child.parent_id).one()
            old_parent.articles.remove(child)
        new_parent.articles.append(child)
        return json.dumps({'responseText': "Category assigned"})

    # @todo remove this function
    @cherrypy.expose
    def buildOrder(self):
        '''A temporary patch to no default set on Article.order. Our javascript requires this value to be not null'''
        categories = Article.list(cherrypy.request.db)
        count = 0
        for article in categories:
            article.order = count
            count +=1 
        return json.dumps(categories, cls=Jsonify(),check_circular=False, skipkeys=True, indent=2)

    @cherrypy.expose
    def setOrder(self):
        '''Accepts an xhr request header X-Admin-setOrder and serializes Article() instances by order with children'''
        data = cherrypy.request.headers.get('X-Admin-Menu-SetOrder')
        data = json.loads(data)
        order=0
        for _id in self.setOrder_generator(data):
            if type(_id) == int:
                article = cherrypy.request.db.query(Article).get(_id)
                if article.parent_id != None:
                    old_parent = cherrypy.request.db.query(Article).filter(Article._id == article.parent_id).one()
                    old_parent.articles.remove(article)
                article.parent_id = None
                article.order = order
                order += 1
                print("int", _id)
            else:
                _tuple = self.setOrder_unwrap(_id)
                a_id = _tuple[-1]
                p_id = _tuple[0]
                article = cherrypy.request.db.query(Article).get(a_id)
                if article.parent_id != None:
                    old_parent = cherrypy.request.db.query(Article).filter(Article._id == article.parent_id).one()
                    old_parent.articles.remove(article)
                parent = cherrypy.request.db.query(Article).get(p_id)
                article.parent_id = parent._id
                article.order = order
                parent.articles.append(article)
                order += 1

        return json.dumps({"responseText": "Order & children set"})

    def setOrder_unwrap(self, aDict):
        for k,v in aDict.iteritems():
            if type(v) == int:
                return k,v
            else:
                return self.setOrder_unwrap(v)

    def setOrder_generator(self, flat):
        '''Explores flattened array of JSON objects
        [0: object
            {"id": "aNum",
            "children": [0: object
            ..]
            }
        ..]
        '''
        for i in flat:
            for k, v in i.items():
                #top level
                if k == "id":
                    yield int(v)
                elif k == "children":
                    for child in self.setOrder_generator(v):
                        _id = int(i["id"])
                        yield {_id: child}


class APIController(object):
    exposed = True
    article = ArticleAPI()
    tag = TagAPI()
    ## Any other APIs can share this mount point

### Config ###

if __name__ == '__main__':
    daemon = Daemonizer(cherrypy.engine)
    daemon.subscribe()
    cherrypy.config.update('config/app.conf')
    SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(ClientController(), '/', config='config/app.conf')
    cherrypy.tree.mount(APIController(), '/admin/api', config='config/api.conf')
    cherrypy.tree.mount(AdminController(), '/admin')

cherrypy.engine.start()
cherrypy.engine.block()