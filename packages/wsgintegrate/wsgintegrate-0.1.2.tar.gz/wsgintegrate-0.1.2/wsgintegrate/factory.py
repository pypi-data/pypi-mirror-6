"""
WSGI integration factory
"""

import os
import sys
from pyloader.factory import IniFactory

class WSGIfactory(IniFactory):
    def __init__(self, inifile, main=''):
        IniFactory.__init__(self, inifile, main)
        self.mtime = os.path.getmtime(self.inifile)

    def __call__(self, environ, start_response):
        """WSGI application"""

        # if the configuration has changed,
        # reload the .ini file
        mtime = os.path.getmtime(self.inifile)
        if mtime > self.mtime:
            print "Reloading '%s': %s > %s" % (self.inifile, mtime, self.mtime)
            try:
                config = self.read(self.inifile)
                self.configure(config)
            except Exception, e:
                print >> sys.stderr, "Error reading '%s': %s" % (self.inifile, e)
            self.mtime = mtime

        app = self.load(self.main)
        return app(environ, start_response)
