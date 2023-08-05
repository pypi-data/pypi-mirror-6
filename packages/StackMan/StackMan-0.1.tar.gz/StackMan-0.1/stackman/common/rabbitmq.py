"""
StackMan
Colton J. Provias - cj@coltonprovias.com
"""

from stackman.stack import StackItem


class RabbitMQ(StackItem):
    """
    Start a RabbitMQ message queue.

    Arguments:
    * command str Command
                  Default: rabbitmq-server
    """
    ready_text = 'broker running'
