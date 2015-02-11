import cherrypy
import json
from sqlalchemy import update
from sqlalchemy.ext.serializer import loads, dumps
from models import Admin, Article, Body, Jsonify
### RESTful API Controllers ###
### ALL RETURNS ON API ROUTES AGONOSTICALLY RETURN `result` ###


class ArticleAPI(object):

    exposed = True
    #@require()
    def GET(self, _id=None, **kwargs):
        '''
        Returns _id if id is supplied OR
        all article records if no id is supplied
        '''
        #supports one non-specific kwarg, womp womp
        if kwargs:
            result = cherrypy.request.db.query(Article).filter_by(**kwargs).all()
            print('**************************')
            return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)
        # if no id is specified, 
        elif _id == None:
            result = Article.list(cherrypy.request.db)
            return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)

        result = cherrypy.request.db.query(Article).get(_id)
        return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)
            
    #@require()
    def POST(self, **kwargs):
        '''
        If authorized, persist a new Article() to session and return it
        No validation strategy implemented, use with caution
        '''
        result = Article()
        data = cherrypy.request.headers.get('X-Ckeditor-New')
        for key in data:
            setattr(result, key, data[key])
        cherrypy.request.db.add(result)
        return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)

    #@require()
    def PUT(self, _id):
        '''
        If authorized, retrieve Article() and persist on session
        No validation strategy implemented, use with caution
        '''
        result = cherrypy.request.db.query(Article).get(_id)
        data = cherrypy.request.headers.get('X-Ckeditor-Edit')
        data = json.loads(data, encoding="utf-8")
        for key in data:
            if key.startswith("body"):
                split = key.split('_')
                _id = split[2]
                result = cherrypy.request.db.query(Body).get(_id)
                setattr(result,'text',data[key])
            else:
                setattr(result,key,data[key])
        return cherrypy.request.db.add(result)


    def DELETE(self, _id=None):
        result = cherrypy.request.db.query(Article).filter(Article._id == _id).delete()
        return result


"""
We probably don't need an image uploading system

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
"""