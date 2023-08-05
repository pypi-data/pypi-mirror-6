"""
StackMan
Application
Colton J. Provias - cj@coltonprovias.com
Created: December 8, 2013

The main application and web handler for StackMan.
"""

import logging
import os
import uuid
import json
from tornado import options, web, ioloop
from .websocket import SocketHandler


options.define('port', default=6760, type=int, metavar='PORT',
               help='Port to bind to.')
options.define('file', default='stackman.stack', type=str, metavar='FILE',
               help='File to load and save stack to.')


class Application(web.Application):
    """ Create and initialize both the WebHandler and the SocketHandler. """
    def __init__(self):
        handlers = [(r'/', WebHandler),
                    (r'/socket', SocketHandler)]
        settings = {'cookie_secret': uuid.uuid4().hex,
                    'static_path': os.path.join(os.path.dirname(__file__),
                                                'static')}
        # Set up the stacks before we init!
        SocketHandler.file = options.options.file
        SocketHandler.load_stacks()
        web.Application.__init__(self, handlers, **settings)


class WebHandler(web.RequestHandler):
    """ Display a simple page...with some messy JavaScript. """
    def get(self):
        self.render('templates/index.html')


def main():
    options.parse_command_line()
    if not os.path.exists(options.options.file):
        logging.warning('Configuration file not found.  Creating.')
        json.dump({'stacks': []}, open(options.options.file, 'w'))
    application = Application()
    application.listen(options.options.port)
    port = str(options.options.port)
    logging.warning('Now running at http://0.0.0.0:' + port)
    ioloop.IOLoop.instance().start()
