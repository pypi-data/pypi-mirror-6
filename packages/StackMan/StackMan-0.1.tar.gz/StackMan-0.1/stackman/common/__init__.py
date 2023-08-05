"""
StackMan
Common Stack Items...I should rename them to stack modules sometime...
Colton J. Provias - cj@coltonprovias.com
"""


PREFIX = 'stackman.common.'


COMMON_ITEMS = [PREFIX + x for x in ['celery.Celery',
                                     'coffeescript.CoffeeScript',
                                     'django.Django',
                                     'flower.Flower',
                                     'postgresql.PostgreSQL',
                                     'pyramid.Pyramid',
                                     'rabbitmq.RabbitMQ',
                                     'rails.RubyOnRails',
                                     'redis.Redis',
                                     'shell.ShellCommand']]
