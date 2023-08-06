"""
front-ends for various WSGI servers
"""

from factory import WSGIfactory

__all__ = ['wsgiref', 'servers', 'paster']

def wsgiref(app, host='0.0.0.0', port=80):
  from wsgiref import simple_server
  server = simple_server.make_server(host=host, port=int(port), app=app)
  server.serve_forever()

servers = {'wsgiref': wsgiref}

try:
  from paste import httpserver
  def paste_server(app, host='0.0.0.0', port=80):
    httpserver.serve(app, host=host, port=port)
  servers['paste'] = paste_server
except ImportError:
  print ("Not adding paste.httpserver; not installed")

def paster(global_conf, **kw):
  """factory for paster"""
  return WSGIfactory(**kw)

