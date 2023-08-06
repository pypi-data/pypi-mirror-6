'''
    Tinkerer-Localpost command line
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Provides central location to control localpost command

    :copyright: Copyright 2013, Nathan Hawkes
    :license: FreeBSD, see LICENCE file
'''
import os
import sys
import argparse
from datetime import datetime
import localpost
from localpost import server, output


def serve_blog(port):
    '''
    Serve the blog at http://localhost:port for local debugging purposes.
    '''
    output.write.info("Serving your blog at %s:%i. Use Ctrl-C to shut down the server." % ('127.0.0.1', port))

    # serve the blog for review
    server.serve(port)
    
    output.write.info("Shutting down the server based on user input.\nFinished.")


def main(argv=None):
    '''
    Parses command line and executes required action.
    '''
    try:
        parser = argparse.ArgumentParser(prog="Tinkerer-Localpost", 
                description="Host your blog locally for review",
                epilog="Before you post, always http://localhost!", 
                usage='localpost [options]')
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-S", "--serve", nargs='?', const=8000, default=8000,
                type=int, metavar='PORT', help="serve blog locally for review at "
                "http://localhost:PORT (default: %(default)i)")
        group.add_argument("--version", action="version",
                version=("Tinkerer-Localpost %s" % localpost.__version__))
        group2 = parser.add_mutually_exclusive_group()
        group2.add_argument("-q", "--quiet", action="store_true",
                help="limit output from localpost")
        group2.add_argument("-v", "--verbose", action="count",
                help="make localpost more talkative (can be used multiple times)")
        parser.add_argument("-o", "--output", metavar="LOGFILE", nargs="?", default=None,
                help="specify a log file location for localpost output")

        command = parser.parse_args(argv)
    except SystemExit as e:
        return e.code
    else:
        output.init(command.quiet, command.verbose, command.output)

        serve_blog(command.serve)

        return 0
