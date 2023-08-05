"""
StackMan
Colton J. Provias - cj@coltonprovias.com
"""

from stackman.stack import StackItem


class CoffeeScript(StackItem):
    """
    Watches your Coffee so you don't have to!

    Arguments:
    * base_command str Base Command
                       Default: coffee
    * input_dir str Input Directory
                    Default: static/coffee
    * output_dir str Output Directory
                     Default: static/js
    """
    ready_text = 'compiled'

    @property
    def command(self):
        i = self.input_dir + '/*.coffee'
        fmap = {'in': i, 'command': self.base_command, 'out': self.output_dir}
        return '{command} -w -c -o {out} {in}'.format_map(fmap)
