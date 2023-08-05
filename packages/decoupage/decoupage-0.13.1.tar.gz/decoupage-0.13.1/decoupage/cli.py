#!/usr/bin/env python

"""
serve directory with decoupage, e.g.

``decoupage --port 8080 /home/jhammel/tmp``

If the directory is not specified, the current working directory is used
"""

import optparse
import os
import socket
import sys

from .formatters import Datestamp, Sort, Up, DirectoryIndicator
from .web import Decoupage
from wsgiref import simple_server

here = os.path.dirname(os.path.realpath(__file__))

class DecoupageServer(Decoupage):
    """serve locally with decoupage"""
    # TODO: deprecate; move Decoupage to a few classes
    # with more flexible formatters
    def __init__(self, *args, **kwargs):
        Decoupage.__init__(self, **kwargs)
        # default formatters
        # TODO: make configurable
        self._formatters = [Sort(),
                            DirectoryIndicator('/'),
                            Up('..'),
                            Datestamp('modified: %m %d, %Y')]
    def get_formatters(self, path):
        return self._formatters


def main(args=sys.argv[1:]):

    # parse command line options
    usage = '%prog [options]'
    parser = optparse.OptionParser(usage=usage, description=__doc__)
    parser.add_option('-p', '--port', dest='port',
                      type='int', default=1977,
                      help="port to serve on [DEFAULT: %default]")
    parser.add_option('-a', '--address', dest='address',
                      default='0.0.0.0',
                      help="address to serve on [DEFAULT: %default]")
    parser.add_option('--no-reload', dest='auto_reload',
                      action='store_false', default=True,
                      help="do not dynamically refresh indices")
    parser.add_option('--no-print-ip', dest='print_ip',
                      action='store_false', default=True,
                      help="do not print resolvable IP address")
    options, args = parser.parse_args(args)
    if not args:
        directory = os.getcwd()
    elif len(args) == 1:
        directory = args[0]
    if len(args) > 1:
            # TODO:
            # allow multiple directories with mount points
            #   e.g. `decoupage [options] directory [directory2=/foo] [...]`
            #   This may be done by creating a temporary directory with appropriate
            #   symbolic links (on OSes that allow them)

        parser.print_help()
        parser.exit(1)
    if not os.path.isdir(directory):
        raise OSError("'%s' is not a directory" % directory)

    # create WSGI app
    # TODO:
    # - allow CLI specification of formatters
    # - template specification
    app = DecoupageServer(directory=directory,
                          auto_reload=options.auto_reload)


    # create server
    # TODO: allow choice amongst server classes
    printable_address = '127.0.0.1' if options.address == '0.0.0.0' else options.address
    server = simple_server.make_server(options.address, options.port, app)
    print 'serving directory %s ( %s ) at \nhttp://%s:%d/' % (directory,
                                                              'file://' + directory, # XXX
                                                              printable_address,
                                                              options.port)
    if options.print_ip:
        # from http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
        hostname = "google.com"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((hostname,80))
        hostname = s.getsockname()[0]
        print "http://%s:%s/" % (hostname, options.port)
        s.close()

    # serve directory contents via decoupage
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
