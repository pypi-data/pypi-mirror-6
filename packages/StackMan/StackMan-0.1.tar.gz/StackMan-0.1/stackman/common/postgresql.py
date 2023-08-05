"""
StackMan
Colton J. Provias - cj@coltonprovias.com
"""

from stackman.stack import StackItem


class PostgreSQL(StackItem):
    """
    Run a PostgreSQL server

    Arguments:
    * base_command str Base Command
                       Default: postgres
    * data_dir str Data Directory
                   Default: /usr/local/var/postgres
    """
    ready_text = 'ready'

    @property
    def command(self):
        return self.base_command + ' -D ' + self.data_dir
