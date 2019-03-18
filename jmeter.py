#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Author:fengdy
# @Email:iamfengdy@126.com
# @DateTime:2019/03/13 10:31


""" jmeter performance test """
__version__ = '1.0'
__history__ = ''' '''
__all__ = []


import os
import argparse
import logging
from datetime import timedelta
from datetime import datetime as dtime
from configparser import ConfigParser, ExtendedInterpolation
import subprocess
import shutil

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(lineno)d] %(levelname)s %(message)s',
        datefmt='%Y%m%d %H:%M:%S',
        filename='result.log',
        filemode='w'
    )
log = logging.getLogger()

SEPARATE_LINE = "*"*24
NEXT_RUN_TS = None
NOW_RUN_TS = None
JMETER_LOG_FILE = "result.txt"
JMETER_RESULT_FOLDER = "html"
SERVER_PORT = '9000'
COMMAND = "jmeter -n -t {file_name} -l "\
          + JMETER_LOG_FILE \
          + " -e -o " \
          + JMETER_RESULT_FOLDER\
          + " -JTHREAD_NUM={thread}" \
            " -JTIMEOUT={timeout}000" \
            " -JSERVER_IP={server_ip}"
LOG_HELP=[
    "",
    "CMD: command",
    "TST: test start time",
    "CST: command start time"
]
COMMAND_ERROR = "Command is wrong!"
COMMAND_OUTPUT_ERROR = "Command ouput is wrong!"


class Command:
    def __init__(self, argument):
        self.file_name = argument.file
        if argument.address.find(':') > 0:
            ip, port = argument.address.split(':')
        else:
            ip = argument.address
            port = SERVER_PORT
        self.address = ':'.join([ip, port])
        self.server_ip = ip 
        self.server_port = port 
        self.thread = argument.thread
        self.timeout = argument.timeout
        self.total = argument.total
        self.interval = argument.interval
        self.command = COMMAND.format(file_name=self.file_name, thread=self.thread, timeout=self.timeout, server_ip=self.server_ip)
        log.setLevel(argument.loglevel.upper())

    def __str__(self):
        _string = "Thread:{} File:{} Timeout:{} Address:{}".format(self.thread, self.file_name, self.timeout, self.address)
        return _string


class Result:
    def __init__(self):
        pass

    def init(self, kwargs):
        if isinstance(kwargs, dict):
            self.__dict__.update(kwargs)


class CommandResult(Result):
    def __init__(self, folder_name, run_time, timestamp=None, success=True, error_count=0):
        self.success = success
        self.run_time = run_time
        self.error_count = error_count
        self.folder_name = folder_name
        self.timestamp = timestamp

    def __str__(self):
        _string = "Folder:{} Error:{} Timestamp:{}, Success:{}".format(self.folder_name, self.error_count, self.timestamp, self.success)
        return _string


class JmeterResult(Result):
    def __init__(self, command):
        self.success = True
        self.max_time = 0
        self.min_time = 0 
        self.error_count = 0
        self.command = command
        self.error_results = []
        self.error_max_time = 0
        self.error_min_time = 0

    def add_error(self, commandresult):
        self.error_results.append(commandresult)
        self.error_count += 1

    def set_max_time(self, ts):
        self.max_time = self.max_time if self.max_time >= ts else ts

    def set_min_time(self, ts):
        self.min_time = self.min_time if self.min_time >= ts else ts

    def set_error_max_time(self, ts):
        self.error_max_time = self.error_max_time if self.error_max_time >= ts else ts

    def set_error_min_time(self, ts):
        self.error_min_time = self.error_min_time if self.error_min_time >= ts else ts

    def add_commandresult(self, commandresult):
        if not commandresult.success:
            self.add_error(commandresult)
            self.set_error_max_time(commandresult.run_time)
            self.set_error_min_time(commandresult.run_time)
        self.set_max_time(commandresult.run_time)
        self.set_min_time(commandresult.run_time)

    def __str__(self):
        _string = "MaxTime:{} MinTime:{} Error:{} ErrorMaxTime:{}, ErrorMinTime:{}, ErrorResult:\n".format(
            self.max_time, self.min_time, self.error_count, self.error_max_time, self.error_min_time)
        _string += "\n".join([ "\t"+str(er) for er in self.error_results])
        return _string


def run_command(command):
    # result = subprocess.check_output(command.split(" "))
    try:
        result = subprocess.check_output(command, shell=True)
        return result.decode()
    except Exception as e:
        log.error(e.msg)
        return None


def analyse_result(message):
    """analyse command result
    :return: run_time, error_count, ts
    """
    run_time = 0
    error_count = 0
    ts = 0
    try:
        for line in message.split("\n"):
            line = line.replace(" ", "")
            if line.count("summary=") > 0:
                _, rt, ec = line.split("=")
                run_time = rt.split("in")[1]
                _, ec = ec.split("Err:")
                error_count, _ = ec.split("(")
                error_count = int(error_count)
                continue
            if line.count("Tidyingup") > 0:
                line = line.split("(")[1]
                line = line.split(")")[0]
                ts = line
                continue
        if run_time.count(":") == 2:
            h, m, s = run_time.split(":")
            run_time = int(h)*3600+int(m)*60+int(s)
        else:
            run_time = 0
    except:
        error_count = COMMAND_OUTPUT_ERROR
        log.error(message)
    return run_time, error_count, ts


def do_finish(folder_path):
    log_path = JMETER_LOG_FILE
    result_path = JMETER_RESULT_FOLDER
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    shutil.move(log_path, folder_path)
    shutil.move(result_path, folder_path)


def run_once(command, folder_name):
    output = run_command(command)
    if output is None:
        run_time = 0
        error_count = COMMAND_ERROR
        timestamp = get_next_time()
    else:
        run_time, error_count, timestamp = analyse_result(output)
    success = error_count == 0
    cr = CommandResult(folder_name,
                       run_time,
                       timestamp=timestamp,
                       error_count=error_count,
                       success=success)
    do_finish(folder_name)
    return cr


def parse_argument():
    """"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="name of jmx file")
    parser.add_argument("-a", "--address", help="ip:port of server or ip")
    parser.add_argument("-t", "--timeout", help="timeout (s)", type=int, default=20)
    parser.add_argument("-c", "--config", help="config path")
    parser.add_argument("-th", "--thread", help="thread num", type=int, default=10)
    parser.add_argument("-to", "--total", help="run total", type=int, default=10)
    parser.add_argument("-in", "--interval", help="run interval (m)", type=int, default=1)
    parser.add_argument("-ll", "--loglevel", help="log level", choices=("debug", "info", "warning", "error"), default="info")
    return parser


def get_next_time(ts=None, interval=0):
    ts_format = "%Y%m%d%H%M"
    now_ts = dtime.now() if ts is None else dtime.strptime(ts, ts_format)
    next_ts = now_ts + timedelta(minutes=interval)
    return dtime.strftime(next_ts, ts_format)


def wait_to_run(interval, func, *args, **kwargs):
    """
    Wait to run
    :param func: function will be executed
    :param interval: wait interval to run
    :param args: args of function
    :param kwargs:
    :return: run(*args, **kwargs)
    """
    global NEXT_RUN_TS
    global NOW_RUN_TS
    ts = get_next_time()
    if NEXT_RUN_TS is not None:
        while NEXT_RUN_TS != ts:
            ts = get_next_time()
    NOW_RUN_TS = ts
    NEXT_RUN_TS = get_next_time(ts, interval)
    return func(*args, **kwargs)


def _run(command):
    assert isinstance(command, Command), "command should be subclass of Command!"
    log.info(SEPARATE_LINE)
    log.info("CMD: "+command.command)
    # TST:test start time
    log.info("TST: "+str(NOW_RUN_TS))
    log.info(SEPARATE_LINE)
    jr = JmeterResult(command.command)
    for i in range(command.total):
        # CST:command start time
        log.debug("CST: "+str(NOW_RUN_TS))
        cr = wait_to_run(command.interval, run_once, command.command, NOW_RUN_TS[4:])
        jr.add_commandresult(cr)
    log.info(jr)


def run_argument(argument):
    command = Command(argument)
    return wait_to_run(1, _run, command)


def run_arguments(_total, _interval,
                  _address, _file, _thread, _timeout, _separator, _loglevel):
    parser = parse_argument()
    for a in _address.split(_separator):
        _argument = ['-to', _total, '-in', _interval, '-a', a, '-ll', _loglevel]
        for f in _file.split(_separator):
            _argument.extend(['-f', f])
            for th in _thread.split(_separator):
                _argument.extend(['-th', th])
                for t in _timeout.split(_separator):
                    _argument.extend(['-t', t])
                    argument = parser.parse_args(_argument)
                    run_argument(argument)


def run_from_config(config_path):
    configParser = ConfigParser(interpolation=ExtendedInterpolation())
    configParser.read(config_path)
    for section in configParser.sections():
        separator = configParser.get(section, 'separator')
        _separator = separator if separator else " "
        _address = configParser.get(section, 'address')
        _file = configParser.get(section, 'file')
        _total = configParser.get(section, 'total')
        _interval = configParser.get(section, 'interval')
        _thread = configParser.get(section, 'thread')
        _timeout = configParser.get(section, 'timeout')
        _loglevel = configParser.get(section, 'loglevel')
        run_arguments(_total, _interval, _address, _file, _thread, _timeout, _separator, _loglevel)


def run_from_argument(argument):
    _separator = argument.separator
    _address = argument.address
    _file = argument.file
    _total = argument.total
    _interval = argument.interval
    _thread = argument.thread
    _timeout = argument.timeout
    _loglevel = argument.loglevel
    run_arguments(_total, _interval, _address, _file, _thread, _timeout, _separator, _loglevel)


def run(argument):
    log.debug("\n".join(LOG_HELP))
    if argument.config and os.path.exists(argument.config):
        run_from_config(argument.config)
    else:
        run_from_argument(argument)


if __name__ == "__main__":
    parser = parse_argument()
    argument = parser.parse_args()
    run(argument)
