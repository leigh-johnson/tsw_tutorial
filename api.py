import cherrypy
import json
import chardet
from sqlalchemy import update
from sqlalchemy.ext.serializer import loads, dumps
from models import Admin, Article, Body_en, Body_fr, Body_de, Tag, Jsonify
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
        if kwargs:
            result = cherrypy.request.db.query(Article).filter_by(**kwargs).all()
            return json.dumps(result, cls=Jsonify(), check_circular=False, skipkeys=True, indent=2)
        #if no kwargs are specified, return the article roll
        result = Article.list(cherrypy.request.db)
        return json.dumps(result, cls=Jsonify(),check_circular=False, skipkeys=True, indent=2)
            
    #@require()
    def POST(self, **kwargs):
        '''
        If authorized, persist a new Article() to session and return it
        No validation strategy implemented, use with caution
        '''
        result = Article()
        bodies = {"body_en":Body_en, "body_fr":Body_fr, "body_de":Body_de}
        for k,v in kwargs.iteritems():
            if k.startswith("body"):
                body = bodies[k]()
                body.text = v
                getattr(result, k).append(body)
            else:
                setattr(result, k, v)
        ### Set each body
        #for key, value in bodies.iteritems():
            #alist = [value]
            #setattr(result, key, alist)
        cherrypy.request.db.add(result)
        return json.dumps({"_id": result._id})

    #@require()
    def PUT(self, _id, new_body=False, **kwargs):
        '''
        If authorized, retrieve Article() and persist on session
        No validation strategy implemented, use with caution
        '''
        result = cherrypy.request.db.query(Article).get(_id)
        bodies = {"body_en":Body_en, "body_fr":Body_fr, "body_de":Body_de}
        if new_body == False:
            for k,v in kwargs.iteritems():
                if k.startswith("body"):
                    # Unpackage request  from Body_$language_$id to Body_$language.get(_id)
                    split = k.split('_')
                    lang = "_".join(split[0:2])
                    body = bodies[lang]
                    _id = split[2]
                    result = cherrypy.request.db.query(body).get(_id)
                    setattr(result,'text', v)
                else:
                    setattr(result,k, v)
        # handle new Body_$lang instance creation
        if new_body == 'True':
            body_fr = Body_fr(text="Empty French section.<br> Click to choose a template & begin editing")
            body_en = Body_en(text="Empty English section.<br> Click to choose a template & begin editing")
            body_de = Body_de(text="Empty German section.<br> Click to choose a template & begin editing")
            result.body_fr.append(body_fr)
            result.body_en.append(body_en)
            result.body_de.append(body_de)
        cherrypy.request.db.add(result)
        return json.dumps({"responseText":"Saved!"})


    def DELETE(self, _id=None):
        result = cherrypy.request.db.query(Article).filter(Article._id == _id).delete()
        return json.dumps({"responseText": "Deleted!"})

class TagAPI(object):
    exposed = True

    def GET(self):
        result = Tag.list(cherrypy.request.db)
        return json.dumps(result, cls=Jsonify(),check_circular=False, skipkeys=True, indent=2)

    def POST(self, **kwargs):
        '''Create a new instance with kwargs'''
        result = Tag()
        for k,v in kwargs.iteritems():
            setattr(result, k, v)
        cherrypy.request.db.add(result)
        return json.dumps({"_id": result._id})

    def PUT(self, _id=None, **kwargs):
        '''Retrieve an instance by _id and update kwargs'''
        result = cherrypy.request.db.query(Tag).get(_id)
        for k,v in kwargs.iteritems():
            setattr(result, k, v)
        cherrypy.request.db.add(result)
        return json.dumps({"responseText": "Updated tag %s" %result._id})

    def DELETE(self, _id=None):
        if _id != None:
            result = cherrypy.request.db.query(Tag).filter(Tag._id == _id).delete()
        return json.dumps({"responseText": "Need to specify an id"})

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