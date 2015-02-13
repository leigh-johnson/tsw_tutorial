import cherrypy
import json
from sqlalchemy import update
from sqlalchemy.ext.serializer import loads, dumps
from models import Admin, Article, Body_en, Body_fr, Body_de, Jsonify
### RESTful API Controllers ###
### ALL RETURNS ON API ROUTES AGONOSTICALLY RETURN `result` ###


class ArticleAPI(object):
    '''To integrate with AJAX requests, API should ALWAYS return valid JSON
    In cases where values are None/null, data should be sanitized or AJAX response expectations should be text and not JSON'''

    exposed = True
    #@require()
    def GET(self, **kwargs):
        '''
        Returns _id if id is supplied OR
        all article records if no id is supplied
        '''
        #supports one non-specific kwarg, womp womp
        if kwargs:
            result = cherrypy.request.db.query(Article).filter_by(**kwargs).all()
            return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)
        #if no kwargs are specified, return the article roll
        result = Article.list(cherrypy.request.db)
        return json.dumps(result, cls=Jsonify(),check_circular=False, skipkeys=True, indent=2)
            
    #@require()
    def POST(self):
        '''
        If authorized, persist a new Article() to session and return it
        No validation strategy implemented, use with caution
        '''
        result = Article()
        data = cherrypy.request.headers.get('X-Ckeditor-New')
        data = json.loads(data, encoding="utf-8")
        bodies = {"body_en":Body_en, "body_fr":Body_fr, "body_de":Body_de}
        for key in data:
            if key.startswith("body"):
                body = bodies[key]()
                body.text = data[key]
                getattr(result, key).append(body)
            else:
                setattr(result, key, data[key])
        ### Set each body
        #for key, value in bodies.iteritems():
            #alist = [value]
            #setattr(result, key, alist)
        cherrypy.request.db.add(result)
        return json.dumps({"responseText": "Created!"})

    #@require()
    def PUT(self, _id):
        '''
        If authorized, retrieve Article() and persist on session
        No validation strategy implemented, use with caution
        '''
        result = cherrypy.request.db.query(Article).get(_id)
        data = cherrypy.request.headers.get('X-Ckeditor-Edit')
        data = json.loads(data, encoding="utf-8")
        bodies = {"body_en":Body_en, "body_fr":Body_fr, "body_de":Body_de}
        for key in data:
            if key.startswith("body"):
                # Unpackage request  from Body_$language_$id to Body_$language.get(_id)
                split = key.split('_')
                lang = "_".join(split[0:2])
                body = bodies[lang]
                _id = split[2]
                result = cherrypy.request.db.query(body).get(_id)
                setattr(result,'text',data[key])
            else:
                setattr(result,key,data[key])
        cherrypy.request.db.add(result)
        return json.dumps({"responseText":"Saved!"})


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