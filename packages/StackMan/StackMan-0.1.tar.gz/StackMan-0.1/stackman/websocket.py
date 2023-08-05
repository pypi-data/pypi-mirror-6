"""
StackMan
WebSocket Handler
Colton J. Provias - cj@coltonprovias.com
"""

import json
import logging
import tornado.websocket
from stackman.stack import Stack, load_item
from stackman.common import COMMON_ITEMS


class SocketHandler(tornado.websocket.WebSocketHandler):
    """ Handles sockets without sticking forks in them.  """
    connections = set()
    stacks = set()

    def allow_draft76(self):
        """ Compat """
        return True

    def open(self):
        """ Welcome our new overlord. """
        logging.info('Client connected')
        SocketHandler.connections.add(self)

    def on_close(self):
        """ Overthrow the overlord. """
        logging.info('Client disconnected')
        SocketHandler.connections.remove(self)

    @classmethod
    def send_message(cls, stack='', sender='', command='', payload=''):
        """ Send a message...which may never be written back. """
        message = json.dumps({'stack': stack,
                              'sender': sender,
                              'command': command,
                              'payload': payload})
        logging.debug('SEND ' + message)
        for conn in cls.connections:
            try:
                conn.write_message(message)
            except:
                logging.error('Could not send message.', exc_info=True)

    def on_message(self, message):
        """ Handle an incoming message, routing as necessary. """
        logging.info('RECV ' + message)
        try:
            message = json.loads(message)
            stack_id = message['stack']
            command = message['command'].lower()
            argument = message['arg']
            if stack_id:
                stack = SocketHandler.stack_by_id(stack_id)
        except ValueError as e:
            logging.warning(e, exc_info=True)
            return False
        try:
            if command == 'start':
                stack.start(argument)
            elif command == 'stop':
                stack.stop(argument)
            elif command == 'kill':
                stack.kill(argument)
            elif command == 'addstack':
                SocketHandler.add_stack(Stack(argument), True)
            elif command == 'removestack':
                SocketHandler.remove_stack(stack, True)
            elif command == 'additem':
                stack.add_item(argument)
            elif command == 'removeitem':
                stack.remove_item(argument)
            elif command == 'moveup':
                stack.move_up(argument)
            elif command == 'movedown':
                stack.move_down(argument)
            elif command == 'save':
                SocketHandler.save()
            elif command == 'reload':
                SocketHandler.load_stacks()
            elif command == 'list':
                self.list_all()
            else:
                logging.warning('Unknown command: ' + command)
        except Exception as e:
            logging.error(e, exc_info=True)

    @classmethod
    def load_stacks(cls):
        """ Load the stacks from the stack file. """
        for stack in cls.stacks:
            logging.info('Shutting down stack ' + stack[0] + ' for reload.')
            stack[1].stop()
        logging.info('Loading stacks from ' + cls.file)
        cls.stacks = set()
        stack_data = json.load(open(cls.file, 'r'))
        for stack in stack_data['stacks']:
            logging.info('Loading stack: ' + stack['name'])
            s = Stack(stack['name'], stack['id'])
            s.load_items(stack['items'])
            cls.add_stack(s, do_save=False)
        cls.list_all()

    @classmethod
    def save(cls):
        """ "Yes, I saved the stacks." ~The Doctor (not really) """
        logging.warning('Saving stacks to ' + cls.file)
        out = {'stacks': []}
        for stack in cls.stacks:
            out['stacks'].append(stack[1].save)
        json.dump(out, open(cls.file, 'w'))

    @classmethod
    def stack_by_id(cls, stack_id):
        """
        Some of these are so obvious by the name, I don't know why I comment.
        """
        for stack in cls.stacks:
            if stack[0] == stack_id:
                return stack[1]
        raise Exception('Failed to find stack ' + stack_id)

    @classmethod
    def list_all(cls):
        """
        List all of the stacks and all of the common item configs.  This is
        meant for the browser.
        """
        stacks = dict()
        items = dict()
        for stack in cls.stacks:
            stacks[stack[0]] = stack[1].dump
        for item in COMMON_ITEMS:
            i = load_item(item)
            items[item] = i._dump_config
        cls.send_message(command='list', payload={'stacks': stacks,
                                                  'items': items})

    @classmethod
    def add_stack(cls, stack, send_update=False, do_save=True):
        """
        Does what it says.  Also, autocomplete gets annoying.  Put a period in
        and it thinks you want to add a function name.__add__()
        """
        if type(stack) == str:
            stack = Stack(stack)
        cls.stacks.add((stack.id, stack))
        stack.set_socket_handler(cls)
        if do_save:
            cls.save()
        if send_update:
            cls.send_message(stack=stack.id, command='addstack',
                             payload=stack.dump)

    @classmethod
    def remove_stack(cls, stack, send_update=False):
        """ Does what it says. """
        stack.stop()
        for item in stack.items:
            stack.remove_item(item._id)
        cls.stacks.remove((stack.id, stack))
        logging.info(cls.stacks)
        cls.save()
        if send_update:
            cls.list_all()
