#!/usr/bin/env python

# XXX legacy WSGIblob code; to be ported [TODO]

"""
web handlers for wsgiblob
"""

import sys
from webob import exc
from webob import Request
from webob import Response

class JSONhandler(object):
  """handles JSON requests"""

  def __init__(self, factory):
    self.factory = factory

  def __call__(self, environ, start_response):
    request = Request(environ)
    if  request.method == 'GET':
      response = Response(content_type='application/json',
                          body=self.factory.json_config())
      return response(environ, start_response)
    elif request.method == 'POST':
      raise NotImplementedError
    else:
      raise NotImplementedError
    
def main(args=sys.argv[1:]):
  from factory import StringFactory
  raise NotImplementedError
  f = StringFactory(config={'':dict(type='app')})

if __name__ == '__main__':
  main()
