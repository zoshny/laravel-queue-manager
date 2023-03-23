import subprocess
from urllib.parse import parse_qsl, urlparse


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


def is_process_running(pid: int):
    '''
    根据pid，判断指定进程是否存在
    '''

    try:
        output = subprocess.check_output(['tasklist', '/FI', f'PID eq {pid}'])
        return f"{pid}".encode('utf-8') in output
    except subprocess.CalledProcessError:
        return False
