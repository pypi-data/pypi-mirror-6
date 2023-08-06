Introduction
=====================

E-Deposit RabbitMQ module for anti-virus.

Examples
--------

Anti-virus client
::

    Python 2.7.3 (default, Jan  2 2013, 13:56:14)
    >>> from edeposit.amqp.antivir import amqpav
    >>> avc = amqpav.AVClient()
    >>> avc
    <amqpav.AVClient instance at 0x7f7414441050>
    >>> message_id = avc.check_file('somefile.ogg')
    Message sent.
    >>> message_id
    '13d80b64-b6ae-4bc2-a42b-4d341ff08499'
    >>> result = avc.get_result(message_id)
    >>> result
    True
    >>> print('File is clean: {}'.format(result))
    File is clean: True
    >>>

Anti-virus server
::

 Python 2.7.3 (default, Jan  2 2013, 13:56:14) 
 >>> from edeposit.amqp.antivir import amqpav
 >>> avs = amqpav.AVServer()
 >>> avs
 <edeposit.amqp.antivir.amqpav.AVServer instance at 0x22285f0>
 >>> avs.run()
  * Message received
 Message: AV Message: fbb4a3e8-b297-4cdb-81c2-1c48a4248d8f
 Headers:
 {   u'header1': u'test'}
 Properties:
 {   'app_id': u'antivirus',
     'application_headers': {   u'header1': u'test'},
     'content_encoding': u'binary',
     'content_type': u'application/octet-stream',
     'message_id': u'fbb4a3e8-b297-4cdb-81c2-1c48a4248d8f',
     'type': u'request'}
 AV result: {'stream': 'Eicar-Test-Signature(69630e4574ec6798239b091cda43dca0:69)'}
  * Message received
 Message: AV Message: e0a616f8-0958-4114-b0e9-ce75b5bc8184
 Headers:
 {   u'header1': u'test'}
 Properties:
 {   'app_id': u'antivirus',
     'application_headers': {   u'header1': u'test'},
     'content_encoding': u'binary',
     'content_type': u'application/octet-stream',
     'message_id': u'e0a616f8-0958-4114-b0e9-ce75b5bc8184',
     'type': u'request'}
 AV result: {'stream': 'Eicar-Test-Signature(69630e4574ec6798239b091cda43dca0:69)'}
 
