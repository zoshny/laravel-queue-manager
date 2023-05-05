import logging
import os
import subprocess
from signal import SIGTERM

import threading
import time

from function import *

# 当前已启动的队列列表
queue_list = {}

# 守护线程退出标志
daemon_thread_exit_flag = threading.Event()


def start_queue(query: dict):
    '''
    启动指定队列监听器
    '''

    # 队列名称
    name = query.get('name')

    # 队列额外执行参数（即`php artisan queue:work`的选项和参数）
    options = query.get('options', '')

    # 要启动的队列进程并发数；默认为1
    count = int(query.get('count', 1))

    # 是否要守护进程的运行（被关闭后会自动启动）
    daemon = bool(query.get('daemon', True))

    if not name:
        return response_fail('启动失败：队列名称(name)不能为空')

    if count < 1:
        return response_fail('启动失败：队列最少启动进程数为1条')

    try:

        # 从队列列表中查询目标队列是否已启动
        target_queue = queue_list.get(name)

        # 目标队列已启动
        if target_queue:
            return response_fail('启动失败：目标队列已启动')

        pids = []

        # 开始遍历创建队列子进程
        for index in range(count):

            worker_name = f'{name}-{index + 1}'

            process = start_queue_process(name, worker_name, options)

            pids.append(process.pid)

        # 保存新的队列信息
        queue_list.setdefault(name, {
            "options": options,
            "count": count,
            "daemon": daemon,
            "pids": pids,
        })

        logging.info(f'队列<{name}>启动成功，数量：{count}条，进程id：{pids}')
        return response_success()

    except Exception as e:
        logging.exception(f'队列<{name}>启动失败，原因: {e}')
        return response_fail('子进程启动失败')


def end_queue(query: dict):
    '''
    结束运行指定
    '''

    name = query.get('name')

    if not name:
        return response_fail('结束失败：队列名称(name)不能为空')

    target_queue = queue_list.get(name)

    if not target_queue:
        return response_fail(f'结束失败: 队列<{name}>未在运行')

    # 提取pids并删除队列记录
    pids = target_queue.get("pids", [])
    del queue_list[name]

    # 遍历进程id列表并结束
    for pid in pids:
        os.kill(pid, SIGTERM)

    logging.info(f'队列<{name}>结束成功，数量：{len(pids)}条，进程id：{pids}')

    return response_success()


def get_queue_status(query: dict):
    '''
    获取指定队列的运行状态
    '''

    name = query.get('name')

    if not name:
        return response_fail('获取失败：队列名称(name)不能为空')

    target_queue = queue_list.get(name)

    if not target_queue:
        return response_success({"status": 0}, message="队列未在运行")

    # 判断所有子进程是否正常
    pids = target_queue.get("pids", [])

    running = 0

    for pid in pids:
        if is_process_running(pid):
            running += 1

    return response_success({"status": 1, "total": len(pids), "running": running}, message=f'目标队列共有{len(pids)}个进程，其中有{running}个正常运行')


def start_daemon():
    '''
    启动队列守护线程
    '''

    # 定义线程worker
    def worker():

        # 每10秒检查一次守护进程的检查
        while True and not daemon_thread_exit_flag.is_set():

            for name in queue_list:

                queue = queue_list[name]

                # 目标队列不需要守护，直接跳过
                if queue.get('daemon') != True:
                    continue

                pids = queue.get('pids', [])

                # 守护成功进程的数量
                count = 0

                # 新的进程列表
                pids_news = []

                # 判断目标队列的进程是否都正常
                for index, pid in enumerate(pids):

                    # 有不正常的进程，需要重新启动一个进行代替
                    if not is_process_running(pid):

                        worker_name = f'{name}-{index + 1}'

                        options = queue.get("options")

                        process = start_queue_process(name, worker_name, options)

                        # 新pid覆盖旧pid
                        pids[index] = process.pid

                        count += 1

                        pids_news.append(process.pid)

                # 守护成功的进程数量大于0
                if count > 0:
                    logging.info(f'队列<{name}>守护成功，自动恢复进程数量：{count}条，进程id: {pids_news}')

            time.sleep(10)

        # 启动线程
    thread = threading.Thread(target=worker, name="queue-daemon")

    thread.start()


def start_queue_process(queue, name, options):
    '''
    启动一个队列进程
    '''

    # 创建php artisan命令
    cmd = ['php', 'artisan', 'queue:work', f'--queue={queue}']

    # 队列自定义名称
    if name:
        cmd += [f'--name={name}']

    # 附加指令
    if options:
        cmd += options.split(',')

    process = subprocess.Popen(cmd, cwd=os.getenv('PROJECT_PATH'))

    return process
