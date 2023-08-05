#!/usr/bin/env python
"""
A minimal Quixote demo.  If you have the 'quixote' package in your Python
path, you can run it like this:

  $ python demo/mini_demo.py

The server listens on localhost:8080 by default.  Debug and error output
will be sent to the terminal.
"""

from quixote.publish import Publisher
from quixote.directory import Directory
import time

last_time = 0

class RootDirectory(Directory):

    _q_exports = ['', 'hello']

    def _q_index(self):
        return '''<html>
                    <body>Welcome to the Quixote demo.  Here is a
                    <a href="hello">link</a>.
                    </body>
                  </html>
                '''

    def hello(self):
        global last_time
        now = time.time()
        print 'took %.4f' % (now - last_time)
        last_time = time.time()
        return '<html><body>Hello world!</body></html>'


def create_publisher():
    return Publisher(RootDirectory(),
                     display_exceptions='plain')


if __name__ == '__main__':
    from quixote.server.simple_server import run
    print 'creating demo listening on http://localhost:8081/'
    run(create_publisher, host='0', port=8081)
