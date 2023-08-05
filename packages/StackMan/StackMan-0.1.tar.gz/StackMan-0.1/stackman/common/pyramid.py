"""
StackMan
Colton J. Provias - cj@coltonprovias.com
"""

from stackman.stack import StackItem


class Pyramid(StackItem):
    """
    pserve kept deadlocking this, so we use gunicorn here insetad.

    Arguments:
    * config str Paste Configuration File
                 Default: development.ini
    * port int Port to bind to
               Default: 6543
    """
    ready_text = 'Listening'

    @property
    def command(self):
        command = 'gunicorn --paster ' + self.config
        command += ' -b 0.0.0.0:' + self.port
        return command
