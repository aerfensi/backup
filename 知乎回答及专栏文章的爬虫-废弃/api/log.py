#!/usr/bin/env python3
# coding=utf-8

"""
简单的log工具，避免每次写脚本都要配置一遍logger
这是一个功能单一的工具，不会有很高的自由度

目前已知的影响比较大的副作用
Formatter的 %(funcName)s 不再起作用了，默认不知道log是哪个函数打印的了
"""

# 理想很丰满，现实很骨感，我TM写个脚本，要什么log？！
# 我不需要把log输出到文件，而且只需要使用debug这一个等级的log，以及一个很简单的log格式
# 目前这个log仅仅是在调试时输出一些信息，并且方便我在发布脚本的时候关掉这些信息的输出

import logging


def getlogger(name: str, save_to_file: bool=True, level:int=logging.DEBUG) -> logging.Logger:
    """
    获得一个logging.logger对象，默认把log同时输出到文件和屏幕，默认log等级为DEBUG
    name: logger名字
    save_to_file: 是否需要输出log到文件，
    level: 设置输出到屏幕的log等级
    """

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)  # log默认等级是INFO，手动设为DEBUG

    fmt = logging.Formatter(
        fmt='%(levelname)s: %(message)s')

    if save_to_file:
        fh = logging.FileHandler(name + r'.log')
        fh.setFormatter(fmt)
        fh.setLevel(logging.DEBUG)
        log.addHandler(fh)
        # 每次拿到logger对象时都会输出这行log到文件，大多数情况下这行log代表这脚本开始执行
        # 但是这行log不需要被输出到屏幕，故先创建FileHandler，再创建StreamHandler
        log.info('---------------------------------------')

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    sh.setLevel(level)
    log.addHandler(sh)

    return log

# 我需要一个默认的logger
_DEFAULT_LOGGER_NAME = 'default_log'


def init_default_logger(save_to_file: bool=True, level: int=logging.DEBUG):
    """
    修改默认logger的行为
    """
    global default_log
    default_log = getlogger(_DEFAULT_LOGGER_NAME, save_to_file, level)


def debug(msg: str):
    global default_log
    try:
        default_log.debug(msg)
    except NameError:
        default_log = getlogger(_DEFAULT_LOGGER_NAME)
        default_log.debug(msg)


def info(msg: str):
    global default_log
    try:
        default_log.info(msg)
    except NameError:
        default_log = getlogger(_DEFAULT_LOGGER_NAME)
        default_log.info(msg)


def warn(msg: str):
    global default_log
    try:
        default_log.warn(msg)
    except NameError:
        default_log = getlogger(_DEFAULT_LOGGER_NAME)
        default_log.warn(msg)


def error(msg: str):
    global default_log
    try:
        default_log.error(msg)
    except NameError:
        default_log = getlogger(_DEFAULT_LOGGER_NAME)
        default_log.error(msg)


def critical(msg: str):
    global default_log
    try:
        default_log.critical(msg)
    except NameError:
        default_log = getlogger(_DEFAULT_LOGGER_NAME)
        default_log.critical(msg)

if __name__ == '__main__':
    debug('hello')
    info('hello')
    warn('hello')
    error('hello')
    critical('hello')
