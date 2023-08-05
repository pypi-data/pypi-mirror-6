"""
StackMan
Colton J. Provias - cj@coltonprovias.com
"""

from stackman.stack import StackItem


class Django(StackItem):
    """
    Runs a django server.

    Arguments:
    * command str Command
                  Default: python manage.py runserver
    """
    ready_text = 'Starting development server'
