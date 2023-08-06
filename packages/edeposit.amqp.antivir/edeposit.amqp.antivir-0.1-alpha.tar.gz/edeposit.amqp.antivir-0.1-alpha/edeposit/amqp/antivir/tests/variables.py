# -*- coding: utf-8 -*-
import edeposit.amqp.antivir
import os
import datetime

BASE_PATH=os.path.dirname(__file__)

edeposit.amqp.antivir = edeposit.amqp.antivir
edeposit.amqp.antivir.Result = edeposit.amqp.antivir.Result
edeposit.amqp.antivir.RequestWithUrl = edeposit.amqp.antivir.RequestWithUrl

UUID = "afdafasd-afdsfasd-fadsljj"
RESPONSE_UUID = "faslll-fasdflfsa-afdfassd"

request_with_clean_file_as_url = edeposit.amqp.antivir.RequestWithUrl(
    UUID = UUID,
    url_of_file = os.path.join(BASE_PATH,'resources','clean-test-file.txt'),
    created = datetime.datetime.now(),
)

request_with_nonclean_file_as_url = edeposit.amqp.antivir.RequestWithUrl(
    UUID = UUID,
    url_of_file = os.path.join(BASE_PATH,'resources','eicar.com'),
    created = datetime.datetime.now(),
)

response_of_clean_test_file = edeposit.amqp.antivir.Result(
    UUID = RESPONSE_UUID,
    UUID_of_content = UUID,
    content_is_clean = True,
    created = datetime.datetime.now()
)

response_of_nonclean_test_file = edeposit.amqp.antivir.Result(
    UUID = RESPONSE_UUID,
    UUID_of_content = UUID,
    content_is_clean = False,
    created = datetime.datetime.now()
)
