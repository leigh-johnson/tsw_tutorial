import cherrypy
import json
from sqlalchemy import update
from sqlalchemy.ext.serializer import loads, dumps
from models import Category, Admin, Img, Article, Jsonify
### RESTful API Controllers ###
### ALL RETURNS ON API ROUTES AGONOSTICALLY RETURN `result` ###


class CategoryAPI(object):

    exposed = True
    #@require()
    def GET(self, _id=None):
        '''
        Returns _id if id is supplied OR
        all category records if no id is supplied
        '''
        if _id == None:
            result = Category.list(cherrypy.request.db)
            return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)
        elif cherrypy.request.db.query(Category).get(_id):
            result = cherrypy.request.db.query(Category).get(_id)
            return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)
            
    #@require()
    def POST(self, **args):
        '''
        If authorized, persist a new Category() to session and return it
        No validation strategy implemented, use with caution
        '''
        result = Category(**kwargs)
        cherrypy.request.db.add(result)
        return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)

    #@require()
    def PUT(self, _id):
        '''
        If authorized, persist on session
        No validation strategy implemented, use with caution
        '''
        result = cherrypy.request.db.query(Category).get(_id)
        data = cherrypy.request.headers.get('X-Ckeditor-Edit')
        data = json.loads(data, encoding="utf-8")
        for key in data:
            setattr(result,key,data[key])
        return cherrypy.request.db.add(result)


    def DELETE(self, _id=None):
        result = cherrypy.request.db.query(Category).filter(Category._id == _id).delete()



class ArticleAPI(object):

    exposed = True

    #@require()
    def GET(self, _id=None):
        '''
        Returns _id if id is supplied OR
        all article records if no id is supplied
        '''
        if _id == None:
            result = Article.list(cherrypy.request.db)
            return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)
        elif cherrypy.request.db.query(Article).get(_id):
            result = cherrypy.request.db.query(Article).get(_id)
            return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)
        return 'Article ID not found.'

    #@require()
    def POST(self, **kwargs):
        '''
        If authorized, persist a new Article() to session and return it
        No validation strategy implemented, use with caution
        '''
        result = Article(kwargs)
        cherrypy.request.db.add(result)
        return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)

    #@require()
    def PUT(self, _id, **kwargs):
        '''
        If authorized, persist .update() on session
        **KWARGS:
        key=value
        No validation strategy implemented, use with caution
        '''
        result = cherrypy.request.db.category.update().where(Article._id == _id).values(**kwargs)
        return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)

    #@require()
    def DELETE(self, _id):
        '''
        Marks object for delete in session
        '''
        result = cherrypy.request.db.query(Article).filter(Article._id == _id).delete()
        return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)



class ImgAPI(object):

    exposed = True

    def GET(self, img_id=None):
        '''
        Returns img_id if id is supplied OR
        all img records if no id is supplied
        '''
        if img_id == None:
            result = Img.list(cherrypy.request.db)
            return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)
        elif cherrypy.request.db.query(Img).get(img_id):
            result = cherrypy.request.db.query(Img).get(img_id)
            return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)
        return 'Img ID not found.'

    def POST(self, **kwargs):
        '''
        If authorized, persist a new Img() to session and return it
        No validation strategy implemented, use with caution
        '''
        result = Img()
        cherrypy.request.db.add(result)
        return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)

    def PUT(self, img_id, **kwargs):
        '''
        If authorized, persist .update() on session
        **KWARGS:
        key=value
        No validation strategy implemented, use with caution
        '''
        result = cherrypy.request.db.query(Img).filter(Img._id == img_id).update(kwargs)
        return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)

    def DELETE(self, img_id):
        '''
        Marks object for delete in session
        '''
        result = cherrypy.request.db.query(Img).filter(Img._id == img_id).delete()
        return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)
