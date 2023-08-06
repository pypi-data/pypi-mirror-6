"""
multi-application dispatcher for WSGI apps
"""

from webob import Request
from webob import exc

class Dispatcher(object):

    def __init__(self, *apps):
        self.apps = apps
        self.codes = set([404])

    def __call__(self, environ, start_response):
        request = Request(environ)
        for app in self.apps:
            try:
                response = request.get_response(app)
                if response.status_int in self.codes:
                    continue
                break
            except exc.HTTPNotFound:
                continue
            except:
                print app
                raise
        else:
            response = exc.HTTPNotFound()
        try:
            return response(environ, start_response)
        except:
            response.headerlist = [(i,str(j)) for i, j in response.headerlist]
            return response(environ, start_response)

