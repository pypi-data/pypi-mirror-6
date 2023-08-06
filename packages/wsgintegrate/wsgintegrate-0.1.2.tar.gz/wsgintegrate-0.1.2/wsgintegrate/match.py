"""
utilities for matching requests
these are just a sample; you can add arbitrary match objects if desired
"""

from webob import Request
from webob import exc

class RequestMatch(object):
  """abstract base class for matching requests"""

  def __init__(self, app):
    self.app = app

  def __call__(self, environ, start_response):
    """WSGI app"""
    if not self.condition(environ):
      raise exc.HTTPNotFound
    return self.app(environ, start_response)

  def condition(self, environ):
    """match condition"""
    return True

class ConditionMatch(RequestMatch):
  """generic environment-based condition-checker"""
  # XXX unused
  def __init__(self, app, condition):
    RequestMatch.__init__(self, app)
    self.condition = condition

### aspect-based checkers

class MatchPath(RequestMatch):
  """match based on PATH INFO"""

  def __init__(self, app, path):
    RequestMatch.__init__(self, app)
    self.path = path

  def match(self, path):
    if path.startswith(self.path):
      # currently only matches with str.startswith;
      # different types of matches could be considered
      return self.path, path[len(self.path):]

  def condition(self, environ): # XXX unused
    return self.match(environ['PATH_INFO']) is not None

  def __call__(self, environ, start_response):
    match = self.match(environ['PATH_INFO'])
    if match is None:
      raise exc.HTTPNotFound
    script_name, path_info = match

    # fix up the environment for downstream applications
    _script_name = environ.get('SCRIPT_NAME')
    _path_info = environ.get('PATH_INFO')
    environ['SCRIPT_NAME'] = script_name
    environ['PATH_INFO'] = path_info

    request = Request(environ)
    response = request.get_response(self.app)

    # unfutz the environ if the resource is not found
    if response.status_int == 404:
        if _script_name is not None:
            environ['SCRIPT_NAME'] = script_name
        environ['PATH_INFO'] = _path_info

    return response(environ, start_response)

class MatchMethod(RequestMatch):
  """match based on request method"""

  def __init__(self, app, methods):
    RequestMatch.__init__(self, app)
    if isinstance(methods, basestring):
      methods = methods.split()
    self.methods = set(methods)

  def condition(self, environ):
    return environ['REQUEST_METHOD'] in self.methods

class MatchHost(RequestMatch):
  """match based on the host and port"""

  def __init__(self, app, host, port=None):
    RequestMatch.__init__(self, app)
    self.wildcard = False
    if host.startswith('*.'):
        self.wildcard = True
        host = host[len('*.'):]
    self.host = host
    self.port = port

  def condition(self, environ):
    host = environ.get('HTTP_HOST')
    if host is None:
        return False
    port = None
    if ':' in host:
        host, port = host.rsplit(':', 1)
    if self.port and port != self.port:
        return False
    if self.wildcard and host.endswith('.' + self.host):
        return True # wildcard
    return host == self.host

class MatchAuthorized(RequestMatch):
  """match if a user is authorized or not"""
  def __init__(self, app, users=None):
    RequestMatch.__init__(self, app)
    self.authorized_users = users
  def condition(self, environ):
    raise NotImplementedError # TODO

class MatchProtocol(RequestMatch):
  """match a given protocol, i.e. http vs https://"""
  def __init__(self, app, protocol):
    self.protocol = protocol
    RequestMatch.__init__(self, app)
  def condition(self, environ):
    raise NotImplementedError # TODO

class MatchQueryString(RequestMatch):
  """
  match a request based on if the right query string parameters are given
  """
  def __init__(self, app, *tags, **kw):
    self.app = app
    self.tags = tags
    self.kw = kw
  def condition(self, environ):
    raise NotImplementedError # TODO

### logical checkers (currently unused)

class AND(RequestMatch):
  def __init__(self, app, condition1, condition2, *conditions):
    RequestMatch.__init__(self, app)
    self.conditions = [condition1, condition2]
    self.conditions.extend(conditions)
  def condition(self, environ):
    for condition in self.conditions:
      if isinstance(condition, RequestMatch):
        if not condition.condition(environ):
          return False
      else:
        if not condition():
          return False
    return True

class OR(RequestMatch):
  def __init__(self, app, condition1, condition2, *conditions):
    RequestMatch.__init__(self, app)
    self.conditions = [condition1, condition2]
    self.conditions.extend(conditions)
  def condition(self, environ):
    for condition in self.conditions:
      if isinstance(condition, RequestMatch):
        if condition.condition(environ):
          return True
      else:
        if condition():
          return
    return False

# string accessible list of conditions
conditions = {'host': MatchHost,
              'method': MatchMethod,
              'path': MatchPath }

class WrapApp(object):
  """match string-based conditions"""

  def __init__(self, conditions=None):
    self.conditions = conditions or globals()['conditions']

  def __call__(self, app, *conditions, **kwargs):
    """
    wrap an app in conditions
    conditions should be a key, value 2-tuple of string, args;
    kwargs should be a dictionary of unordered conditions,
    likewise of the form string, args.
    use *conditions if order is important, otherwise kwargs
    """

    # determine the condition
    conditions = list(conditions)
    if kwargs:
      conditions.extend(kwargs.items())

    # wrap the application
    for condition, args in conditions:
      assert condition in self.conditions, 'Condition "%s" unknown' % condition
      app = self.conditions[condition](app, args)
    return app

# convenience invocation
wrap = WrapApp(conditions)

