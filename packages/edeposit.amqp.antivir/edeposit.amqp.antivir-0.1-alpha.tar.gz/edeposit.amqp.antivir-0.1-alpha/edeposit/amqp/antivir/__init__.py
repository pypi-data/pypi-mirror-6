# This package may contain traces of nuts
from collections import namedtuple


class RequestWithUrl(namedtuple("RequestWithUrl",['url_of_file',
                                                  'UUID',
                                                  'created',
                                              ])):
    pass

class ResultWithData(namedtuple("ResultWithData",['content_is_clean',
                                                  'UUID',
                                                  'UUID_of_content',
                                                  'created',
                                                  'serialization_of_data',
                                                  'data',
                                              ])):
    pass

class Result(namedtuple("Result",['content_is_clean',
                                  'UUID',
                                  'UUID_of_content',
                                  'created',
                              ])):
    """
    valid: [True | False]
    producent: type Producent
    publication: type Publication
    """
    pass

def submit_request(request):
    return True


def convert_amqp_result(data, properties, headers):
    return None
