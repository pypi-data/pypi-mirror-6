"""
StackMan
Colton J. Provias - cj@coltonprovias.com
"""

from stackman.stack import StackItem


class Celery(StackItem):
    """
    Celery eats RabbitMQs...okay.  Anyway, start a Celery worker.

    Arguments:
    * base_command str Base Command
                       Default: celery
    * module str Celery Module
                 Default: project.celery
    * enable_beats bool Enable Celery Beats
                 Default: True
    """
    ready_text = 'ready'

    @property
    def command(self):
        command = [self.base_command, '-A', self.module, 'worker']
        if self.enable_beats:
            command.append('-B')
        return ' '.join(command)
