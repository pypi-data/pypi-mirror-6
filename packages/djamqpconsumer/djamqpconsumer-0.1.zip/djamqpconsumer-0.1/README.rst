What is this
============

Adds a custom command which opens a blocking connection with an AMQP server and passes messages to a callback fuction

Settings
--------

This settings are requiered for the command run

COM_BROKER = "AMQP server ip"
COM_VHOST = "AMQP server Virtual Host"
COM_USERNAME = "Username"
COM_PASSWORD = "Password"
COM_QUEUE = 'Which queue listen to'
CONSUMER_CALLBACK = 'Path to the callback func. ex.: djamqpconsumer.printconsumer.printdata'

Install
-------

pip install djamqpconsumer

Usage
-----

Add djamqpconsumer to your INSTALLED_APPS
run manage.py consumer
