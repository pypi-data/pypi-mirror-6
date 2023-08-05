=====
Bonzo
=====

About
=====

Bonzo is a minimalistic SMTP Proxy built on top of Tornado_.

.. code-block:: python

   import tornado.ioloop
   import email

   from bonzo.smtpserver import SMTPServer


   def receive_message(message):
       print "New received message: "
       print "From: " + message['from']
       print "Subject: " + message['subject']
       for line in email.iterators.body_line_iterator(message):
           print line

   SMTPServer(receive_message).listen(25)
   tornado.ioloop.IOLoop.instance().start()

Installation
============

You can to use pip_ to install Bonzo::

   $ pip install bonzo

Or using last source::

   $ pip install git+git://github.com/puentesarrin/bonzo.git

.. _Tornado: http://tornadoweb.org
.. _pip: http://pypi.python.org/pypi/pip