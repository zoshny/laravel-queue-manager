import logging
import os
import subprocess
from signal import SIGTERM

from function import *

# 队列记录器；确保每个队列只会有一个子进程存在
queue_map = {}


def start_queue(query: dict):
    '''
    启动指定队列监听器
    '''

    queue = query.get('queue')
    params = query.get('params', '')

    if not queue:
        return response_fail('缺少参数: queue')

    try:

        # 目标队列已存在，则先关闭
        # !!!注意，这里会强制关闭，不会等待队列当前的任务结束!!!
        if (queue_map.get(queue)):
            logging.info(f'kill queue <{queue}> old pid: {queue_map.get(queue)}')
            os.kill(queue_map.get(queue), SIGTERM)
            del queue_map[queue]

        cmd = ['php', 'artisan', 'queue:work', f'--queue={queue}']

        if (params):
            cmd += params.split(',')

        # 在子进程中启动队列监听器
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=os.getenv('PROJECT_PATH')
        )

        queue_map.setdefault(queue, process.pid)

        logging.info(f'start queue: <{queue}> success, pid: {process.pid}')

        return response_success()

    except Exception as e:
        logging.info(f'start queue: <{queue}> failed, error: {e}')

        return response_fail('子进程启动失败')


def end_queue(query: dict):
    '''
    结束运行某队列
    '''

    queue = query.get('queue')

    if not queue:
        return response_fail('缺少参数: queue')

    if not queue_map.get(queue):
        return response_fail(f'队列: <{queue}>未在运行')

    os.kill(queue_map.get(queue), SIGTERM)

    logging.info(f'shutdown queue: <{queue}> success')

    return response_success()


def get_queue_status(query: dict):
    '''
    获取指定队列的运行状态
    '''

    queue = query.get('queue')

    if not queue:
        return response_fail('缺少参数: queue')

    if not queue_map.get(queue):
        return response_success({"status": 0, "flag": "STOPPED", "explain": "未在运行"})

    # 判断子进程是存在
    if is_process_running(queue_map.get(queue)):
        return response_success({"status": 1, "flag": "RUNNING", "explain": "正在运行"})

    # 进程pid存在在map中，但并未在系统中运行
    else:
        return response_success({"status": -1, "flag": "EXCEPTION", "explain": "运行异常"})
