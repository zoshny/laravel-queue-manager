#!/usr/bin/python

import http.server
import json
import logging
import os
import socketserver
from datetime import datetime

from dotenv import load_dotenv

from action import *
from function import *

today = datetime.today()


def logging_init():
    '''
    初始化日志记录器
    '''

    if not os.path.exists("log"):
        os.makedirs("log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler("log/" + today.strftime("%Y-%m-%d") + ".log"),
            logging.StreamHandler()
        ]
    )


def check_env():
    '''
    环境变量文件检查
    '''

    default_env = "# http server port\nPORT=5280\n\n"
    default_env += "# laravel project root path\nPROJECT_PATH=\n\n"

    if not os.path.isfile('.env'):
        with open('.env', "w") as f:
            f.write(default_env)


def start_http_server():

    port = int(os.getenv('port') or 5280)

    class RequestHandler(http.server.SimpleHTTPRequestHandler):

        server_version = "Laravel-Queue-Manager/1.0"

        sys_version = ""

        def do_GET(self):

            path, query = parse_url(self.path)

            # 根据请求路径执行相应的方法
            response = {}

            if (path == '/api/startQueue'):
                response = start_queue(query)

            elif (path == '/api/endQueue'):
                response = end_queue(query)

            else:
                response = {"code": 404, 'message': '请求接口不存在'}

            logging.debug("Received GET request: %s", self.path)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(json.dumps(response).encode('utf-8'))

        def log_request(self, code='-', size='-'):
            pass

    with socketserver.TCPServer(("", port), RequestHandler) as httpd:

        logging.info(f"Serving at http://0.0.0.0:{port}/")

        httpd.serve_forever()


if __name__ == "__main__":
    logging_init()
    check_env()
    load_dotenv()

    start_http_server()
