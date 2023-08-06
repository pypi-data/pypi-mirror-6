import pika

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import logging

class Command(BaseCommand):
    args = "debug"
    help = 'AMQP consumer'
    
    debug = False
    callback = None
    host = None
    virtual_host = None
    user_name = None
    user_pass = None
    queue = None
    log = logging.getLogger(__name__)
    
    def setup(self, *args, **kwargs):
        if 'debug' in args:
            self.debug = True
        self.host = getattr(settings, 'COM_BROKER', None)
        self.virtual_host = getattr(settings, 'COM_VHOST', None)
        self.user_name = getattr(settings, 'COM_USERNAME', None)
        self.user_pass = getattr(settings, 'COM_PASSWORD', None)
        self.queue = getattr(settings, 'COM_QUEUE', None)
        if not (self.host and self.virtual_host and self.user_name and self.user_pass and self.queue):
            raise ImproperlyConfigured
        callbackfunc_path = getattr(settings, 'CONSUMER_CALLBACK', None)
        if not callbackfunc_path:
            raise ImproperlyConfigured
        else:
            parts = callbackfunc_path.split('.')
            module = __import__('.'.join(parts[:-1]), fromlist=[parts[-1]])
            self.callback = getattr(module, parts[-1])
            if not(callable(self.callback)):
                   raise ImproperlyConfigured
        self.log.info(u"------ Consumer setup ------")
        self.log.info(u"- Host: " + self.host + u" -")
        self.log.info(u"- VH: " + self.virtual_host + u" -")
        self.log.info(u"- Username: " + self.user_name + u" -")
        self.log.info(u"- Password: " + self.user_pass + u" -")
        self.log.info(u"- Queue: " + self.queue + u" -")
        self.log.info(u"- Callback: " + str(self.callback) + u" -")
            
    def task_do(self,channel, method, header_frame, body):
        result = {}
        if self.debug:
            self.log.info(u"New task" + body)
        try:
            result = self.callback(header_frame, body)
        except Exception, e:
            self.log.error(u"ERROR on callback function: " + str(e))
        status = result.get('result', 0)
        msg = result.get('msg', '')
        retry = result.get('retry', True)
        if status == 1:
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            if self.debug:
                self.log.info('Retrying task. Reason: %s, task: %s, requeue: %s' % (msg, body, str(retry)))            
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=retry)
        return 1
    
    def monitor(self):
        credentials = pika.PlainCredentials(self.user_name, self.user_pass)
        parameters = pika.ConnectionParameters(host=self.host, virtual_host=self.virtual_host,
                                               credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=self.queue)
        channel.basic_consume(self.task_do, queue=self.queue)
        if self.debug:
            self.log.info(u"Start consuming queue...")
        channel.start_consuming()
        
    def handle(self, *args, **options):
        self.setup(*args)
        self.monitor()
