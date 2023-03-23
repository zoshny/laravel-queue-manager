from urllib.parse import urlparse, parse_qsl


def response_success(data=None, message=""):
    '''
    返回一个成功响应
    '''

    response = {"code": 200}

    if not message == "":
        response.setdefault("message", message)

    if not data == None:
        response.setdefault("data", data)

    return response


def response_fail(message, data=None, code=500):
    '''
    返回一个失败响应
    '''

    response = {"code": code}

    if not message == "":
        response.setdefault("message", message)

    if not data == None:
        response.setdefault("data", data)

    return response


def parse_url(url):
    '''
    解析url
    '''

    parsed_url = urlparse(url)
    path = parsed_url.path
    query = parsed_url.query
    query = dict(parse_qsl(query))
    return path, query
