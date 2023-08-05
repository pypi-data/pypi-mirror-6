"""
StackMan
Colton J. Provias - cj@coltonprovias.com
"""

from stackman.stack import StackItem


class Redis(StackItem):
    """
    Initializes a redis server.

    Arguments:
    * command (str) Command
                    Default: redis-server
    """
    ready_text = 'ready'
