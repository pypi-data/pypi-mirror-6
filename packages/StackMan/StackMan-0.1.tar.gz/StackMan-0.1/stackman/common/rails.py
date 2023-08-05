"""
StackMan
Colton J. Provias - cj@coltonprovias.com
"""

from stackman.stack import StackItem


class RubyOnRails(StackItem):
    """
    Ruby on Rails support

    Arguments:
    * command str Command
                  Default: rails server
    """
    ready_text = 'WEBrick::HTTPServer#start:'
