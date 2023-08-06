'''
    espressocup.py (C) 2014 Daniel Fairhead
    "A Microframework for when Flask seems a bit heavy".
    -----------------------------------------------------------
    Intial testing / alpha state.
    -----------------------------------------------------------
    MIT Licence.


'''

import json
import traceback
from datetime import datetime
import os.path
import traceback
from os import walk
import magic

try:
    import re2 as re
except:
    import re


# 'fake' exports functions (to keep pylint, rope, IDEs, etc happy)
def render_template(template_name, *vargs, **kwargs):
    ''' Render a simple template in your application '''
    pass

def jsonify(inputdict):
    ''' Render a dict to JSON '''
    # handled by the request handler later on, so there's no point here, really.
    return inputdict

request = {}

################################################################################
#
# Internal utility bits and pieces:
#

def allfiles(root):
    ''' generator to find all files within this directory '''
    for pathname, _, files in walk(root):
        for filename in files:
            yield os.path.join(pathname, filename)

def json_serial(obj):
    ''' used by jsonify (etc) to convert things into JSON that don't go
        automatically. '''

    if isinstance(obj, datetime):
        return obj.isoformat()

_basic_mimetypes={
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/js',
    '.json': 'application/JSON',
    '.xml': 'application/XML',
    '.rss': 'application/XML',
    }

def _mimetype(filename):
    try:
        _, ext = os.path.splitext(filename)
        return _basic_mimetypes[ext]
    except KeyError:
        return magic.from_file(filename, mime=True)

class Config(object):
    ''' Flask-like 'config' object '''

    _config = {}

    def from_object(self, ob):
        self._config = ob

    def get(self, name, default):
        ''' get method for config... '''

        try:
            return getattr(self._config, name)
        except KeyError:
            return default
        except AttributeError:
            return default

    def __getitem__(self, key):
        return getattr(self._config, key)

    def __setitem__(self, key, value):
        return setattr(self._config, key, value)

class Application(object):
    ''' a very simple almost-flaskish application class '''

    def __init__(self, appname):
        ''' initialise the routing... '''

        self.simpleroutes = {}
        self.reroutes = {}
        self.config = Config()
        self.appname = appname
        self.templates = {}

        if os.path.exists(appname):
            before = os.getcwd()
            os.chdir(appname)

            self._load_templates()
            self._load_statics()

            os.chdir(before)


    def _load_templates(self):
        ''' unlike flask, espressocup loads all templates on application
            load.  this is that. '''

        for filename in allfiles('templates'):
            name = os.path.basename(filename)

            filetype = _mimetype(filename)

            with open(filename, 'r') as fh:
                self.templates[name] = (fh.read(), filetype)

    def _load_statics(self):
        ''' unlike flask, espressocup caches names and mimetypes of all
            static assets.  this is done on application load. '''

        def make_static_handler(fullpath):
            ''' return a static handler with the full path closed into it '''

            def this_static(request):
                ''' dead simple static handler '''
                with open(fullpath,'r') as fh:
                    return ('200 OK', filetype, fh.read())

            return this_static

        for filename in allfiles('static'):
            fullpath = os.path.abspath(filename)

            filetype = _mimetype(filename)

            self.simpleroutes['/' + filename] = make_static_handler(fullpath)

    def render_template(self, template_name, vargs, kwargs):
        ''' render a template, and return a response '''

        try:
            template, template_type = self.templates[template_name]
        except KeyError:
            return ('404 Template Not Found', 'text/plain',
                    'Template (%s) not found!' % template_name)

        return ('200 OK', template_type,
                template.format(*vargs, **kwargs))

    def route(self, rule, **options):
        ''' create a route decorator '''

        def template_renderer(template_name, *vargs, **kwargs):
            return self.render_template(template_name, vargs, kwargs)

        def decorator(function):
            ''' the decorator itself... '''

            def routed_function(environ):
                ''' the function that actually gets called... '''
                # magic - insert 'request' & 'render_template' into the
                # function's globals scope.
                # I don't know if this is a good idea or not... it's
                # certainly simpler than flask's RequestContext stack...

                function.func_globals['request'] = environ
                function.func_globals['render_template'] = template_renderer
                return function()

            self.simpleroutes[rule] = routed_function
            return function # Note : we return the actual function,
                            #        not the 'routed' version, so the
                            #        decorator doesn't actually change the
                            #        function, and then decorators can be
                            #        chained.
        return decorator

    def incoming(self, environ, start_response):
        ''' when requests come in, they get sent here '''

        # defaults:
        response_headers = [('Content-type', 'text/html')]
        status = '200 OK'

        try:
            resp = self.simpleroutes[environ['PATH_INFO']]
        except KeyError:
            status = '404 Not Found'
            data = "Sorry, this route was not defined.<br/>" \
                   "<pre>%s</pre><hr/><pre>%s</pre>" % \
                        (environ['PATH_INFO'], self.simpleroutes)

            start_response(status, response_headers)
            return [data]

        try:
            data = resp(environ)
        except Exception as e:
            status = '500 Server Error'
            data = "Sorry, something went wrong!<br/>" \
                   "<pre>%s</pre><hr/><pre>%s</pre>" % \
                        (str(e), traceback.format_exc())
            traceback.print_exc()

        if isinstance(data, dict):
            response_headers = [('Content-type', 'application/JSON')]
            data = json.dumps(data, default=json_serial)
        elif isinstance(data, tuple):
            status, content_type, data = data
            response_headers = [('Content-type', content_type)]

        start_response(status, response_headers)
        return [data]

    def __call__(self, environ, start_response):
        try:
            return self.incoming(environ, start_response)
        except Exception as e:
            start_response('500 Error', [('Content-type', 'text/plain')])
            return ['Error: %s.\n%s' % (e, traceback.format_exc()) ]


if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer

    app = Application('.')

    @app.route('/')
    def index():
        return render_template('none.html', data=request)

    @app.route('/json')
    def j():
        return {"data":"stuff"}

    WSGIServer(('', 8000), app).serve_forever()
