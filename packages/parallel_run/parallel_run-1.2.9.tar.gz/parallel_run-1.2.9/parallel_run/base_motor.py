#!/usr/bin/env python
#coding:utf8
#author:zhoujingjiang
#date:2014-1-3

#标准库模块
from optparse import OptionParser
import os
import multiprocessing
import signal
import sys
import traceback

#自定义模块
from tools import config2dict, load_module
from base_manager import BaseManager 

#是否进行事件循环 
WILL_RECV = True

def hook_signal():
    #SIGINT，SIGTERM，SIGQUIT - ignore
    #SIGUSR1 - warm shutdown
    #SIGUSR2 - cold shutdown
    def on_ignore_sig(sn, fo):
        '''忽略信号处理函数'''
        pass

    def on_sigusr1(sn, fo):
        '''sigusr1信号处理函数'''
        #将进行事件循环的标志设置为False
        global WILL_RECV
        WILL_RECV = False

    def on_sigusr2(sn, fo):
        '''sigusr2信号处理函数'''
        #退出程序
        sys.exit(1)

    signal.signal(signal.SIGINT, on_ignore_sig)
    signal.signal(signal.SIGTERM, on_ignore_sig)
    signal.signal(signal.SIGQUIT, on_ignore_sig)
    signal.signal(signal.SIGUSR1, on_sigusr1)
    signal.signal(signal.SIGUSR2, on_sigusr2)

def arg_parse():
    '''解析命令行参数'''
    #默认的配置文件的路径
#    default_config = os.path.join(os.path.dirname(
#                os.path.abspath(__file__)), 'default.cfg')

    options = OptionParser()
    options.add_option('-f', '--config_file', dest='config_file', 
#                        default=default_config,
                        help='path of config file')
    options, _ = options.parse_args()
    return options

def sync_process(processes):
    for process in processes:
        try:
            print 'process is', process
            returns = process.get()
            print 'result is', returns
        except Exception, e:
            traceback.print_exc()

def start():
    '''启动器'''
    #信号捕捉
    hook_signal()

    options = arg_parse()
    #将logger添加到option
    options.logger = multiprocessing.get_logger()

    #将配置读进字典
    common_config = config2dict(options.config_file, 'common')
    options.config_file = os.path.abspath(options.config_file)

    #切换工作目录
    main_work_dir = common_config['main_work_dir'].strip("' \"") if \
            'main_work_dir' in common_config else None
    if main_work_dir is not None and os.path.isdir(main_work_dir):
        os.chdir(main_work_dir)

    #增加模块搜索路径
    sys.path.extend(filter(os.path.isdir, map(lambda p : os.path.abspath(p.strip("\" '")), 
                            common_config['main_sys_path'].split(',')))
                            if 'main_sys_path' in common_config else [])
    cur_dir = os.path.abspath(os.curdir)
    if cur_dir not in sys.path:
        sys.path.append(cur_dir)

    #获取manager
    manager_path = [common_config['manager_path'].strip("' \"")] \
            if 'manager_path' in common_config else None
    manager_module = common_config['manager_module'].strip("' \"")
    manager_app = common_config['manager_app'].strip("' \"")
    manager = getattr(load_module(manager_module, manager_path), manager_app)
    if not isinstance(manager, BaseManager):
        raise Exception("manager_app should be subclass of BaseManager")

    #获取receiver及其参数
    receiver_path = [common_config['receiver_path'].strip("' \"")] if \
            'receiver_path' in common_config else None
    receiver_module = common_config['receiver_module'].strip("' \"")
    receiver_app = common_config['receiver_app'].strip("' \"")
    receiver_app_args = common_config['receiver_app_args'].strip("' \"")
    receiver = getattr(load_module(receiver_module, receiver_path), receiver_app)
    receiver_args = getattr(load_module(receiver_module, receiver_path), 
                                receiver_app_args)
    assert hasattr(receiver_args, 'args') and hasattr(receiver_args, 'kwargs'), \
            'receiver_args must have attribute : args and kwargs'
    
    #将进程pid写进文件
    print 'pid of main process is', os.getpid()
    with open(common_config['pid_file'], 'wb') as fd:
        fd.write(str(os.getpid()))

    #生成进程池对象
    process_pool = multiprocessing.Pool(int(common_config['pool_size']))

    #每fork will_sync个子进程，主进程会与子进程同步
    will_sync = int(common_config['will_sync'].strip('\' "'))
    assert will_sync > 0, 'will_sync should be a positive integer'

    #处理事件循环
    processes = []
    while WILL_RECV:
        try:
            messages = receiver(*receiver_args.args, **receiver_args.kwargs)
        except Exception, e:
            print 'error accurs while getting messages :', e
        else:
            for msg in messages:
                options.message = msg
                process = process_pool.apply_async(manager, (options, ))
                processes.append(process)

            if len(processes) == will_sync:
                sync_process(processes)
                processes = []
    #end while
    sync_process(processes)

    #wait进程池中的进程，防止zombie
    process_pool.close()
    process_pool.join()

if __name__ == '__main__':
    start()

