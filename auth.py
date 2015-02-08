## -*- coding: utf-8 -*-
import cherrypy
import urllib
import os
import hashlib
from cgi import escape
from models import Admin
from mako.template import Template
from mako.lookup import TemplateLookup


path = os.path.abspath(os.path.dirname(__file__))
lookup = TemplateLookup(directories=[os.path.join(os.path.abspath(os.curdir)+'/view')], output_encoding='utf-8',collection_size=500)

SESSION_KEY = '_cp_username'

def check_credentials(username, password):
    '''Verifies creds
    Returns None on success or raises http error on failure'''
    for admin in cherrypy.request.db.query(Admin):
        if username == admin.username:
            #if admin.password == hashlib.sha1(password).hexdigest():
            if admin.password == password:
                return 'Good password'
            else:
                return admin.password, ' ', password
    return '%s does not exist' % username

def check_auth(*args, **kwargs):
    '''Checks config for auth.require
    If found and not None, login is required
    entry is evaluated as set of conditions'''
    conditions = cherrypy.request.config.get('auth.require', None)

    #get_params = urllib.quote(cherrypy.request.request_line.split()[1])
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                #Conditions are callables that return True or False
                if not condition():
                    raise cherrypy.HTTPRedirect('login')
        else:
            raise cherrypy.HTTPRedirect('login')

cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def require(*conditions):
    '''Decorator to append conditions to auth.reuiqre config variable'''
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth_require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate

## Conditions are callables that return True 
## if the user fulfils, False otherwise
## Current username available via cherrypy.request.login

def isSomeCondition(username):
    return username is SomeCondition

### Auth Controller ###

class AuthController(object):
    def on_login(self, username):
        '''Called on successful login'''
        pass
    def on_logout(self, username):
        '''Called on logout'''
        pass

    def get_loginform(self, username, msg="Need an account? Contact Romain", from_page='/'):
        username = escape(username, True)
        from_page = escape(from_page, True)
        #mako template
        template = lookup.get_template("login.html")
        return template.render(msg=msg)


    @cherrypy.expose
    def login(self, username=None, password=None, from_page='/'):
        if username is None or password is None:
            return self.get_loginform("", from_page=from_page)

        error_msg = check_credentials(username, password)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        else:
            cherrypy.session.regenerate()
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            raise cherrypy.HTTPRedirect(from_page or '/')

    @cherrypy.expose
    def logout(self, from_page='/'):
        sess = cherrypy.sessionusername = session.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or '/')

    @cherrypy.expose
    def create(self, username, password):
        #password=hashlib.sha1(password).hexdigest()
        result = Admin(username=username, password=password)
        cherrypy.request.db.add(result)
        return 'Created user %s' % username

    @cherrypy.expose
    def delete(self, username):
        result = cherrypy.request.db.query(Admin).filter(username==username).delete()
        return result