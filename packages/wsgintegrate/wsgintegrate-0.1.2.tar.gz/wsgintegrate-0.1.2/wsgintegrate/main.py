#!/usr/bin/env python

"""
command line interface for wsgintegrate.
serves an application from a .ini file
(really, a DAG)
"""

import sys
from factory import WSGIfactory
from optparse import OptionParser
from server import servers

def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line options
    usage = '%prog [options] config-file'
    parser = OptionParser(usage=usage, description=__doc__)
    parser.add_option('-a', '--app', dest='app', default='',
                      help='which app to serve from the configuration')
    parser.add_option('-p', '--port', dest='port',
                      type='int', default=80,
                      help='which port to serve on, if server not specified in configuration')
    parser.add_option('--list-apps', dest='list_apps',
                      action='store_true', default=False,
                      help='list the WSGI apps available in the configuration')
    parser.add_option('--print-json', dest='print_json',
                      action='store_true', default=False,
                      help='print JSON format of the configuration')
    parser.add_option('--print-ini', dest='print_ini',
                      action='store_true', default=False,
                      help='print .ini format of the configuration')
    if len(servers) > 1:
        parser.add_option('-s', '--server', dest='server',
                          choices=servers.keys(), default='wsgiref',
                          help="which WSGI server to use [Choices: {}]".format(', '.join(servers.keys())))
    options, args = parser.parse_args(args)

    # check for single configuration file
    if len(args) != 1: # TODO: could munge multiple configs
        parser.print_usage()
        parser.exit()
    config = args[0]

    # create a factory from configuration
    # TODO: interpret if the configuration is .ini, JSON, etc
    factory = WSGIfactory(config, main=options.app)

    # print configuration, if specified
    if options.list_apps:
        for app in sorted(factory.config.keys()):
            print app
        return
    if options.print_json:
        print factory.json_config()
        return
    if options.print_ini:
        print factory.ini_config()
        return

    # serve it
    server_name = getattr(options, 'server', 'wsgiref')
    print ("Serving with {}".format(server_name))
    server = servers[server_name]
    print ('http://localhost:%d/' % options.port)
    server(app=factory.load(), port=options.port)

if __name__ == '__main__':
  main()
