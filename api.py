import cherrypy
import json
from models import Category, Admin, Img, Article, Jsonify
### RESTful API Controllers ###
### ALL RETURNS ON API ROUTES AGONOSTICALLY RETURN `result` ###

class CategoryAPI(object):

    exposed = True
    #@require()

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
            
    #@require()
    def POST(self, **kwargs):
        '''
        If authorized, persist a new Category() to session and return it
        No validation strategy implemented, use with caution
        '''
        result = Category(kwargs)
        cherrypy.request.db.add(result)
        return json.dumps(result, cls=Jsonify)

    #@require()
    def PUT(self, category_id, **kwargs):
        '''
        If authorized, persist .update() on session
        **KWARGS:
        key=value
        No validation strategy implemented, use with caution
        '''
        result = cherrypy.request.db.query(Category).filter(Category.id == category_id).update(kwargs)
        return json.dumps(result, cls=Jsonify)

    #@require()
    def DELETE(self, category_id):
        '''
        Marks object for delete in session
        '''
        result = cherrypy.request.db.query(Category).filter(Category.id == category_id).delete()
        return json.dumps(result, cls=Jsonify)


class ArticleAPI(object):

    exposed = True

    #@require()
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

    #@require()
    def POST(self, **kwargs):
        '''
        If authorized, persist a new Article() to session and return it
        No validation strategy implemented, use with caution
        '''
        result = Article(kwargs)
        cherrypy.request.db.add(result)
        return json.dumps(result, cls=Jsonify)

    #@require()
    def PUT(self, article_id, **kwargs):
        '''
        If authorized, persist .update() on session
        **KWARGS:
        key=value
        No validation strategy implemented, use with caution
        '''
        result = cherrypy.request.db.query(Article).filter(Article.id == article_id).update(kwargs)
        return json.dumps(result, cls=Jsonify)

    #@require()
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