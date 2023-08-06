# -*- coding: utf-8 -*-

from .log import logger


def safe_call(func, *args, **kwargs):
    """
    安全调用
    """
    try:
        return func(*args, **kwargs)
    except Exception, e:
        logger.error('exc occur. e: %s, func: %s', e, func, exc_info=True)
        # 调用方可以通过 isinstance(e, BaseException) 来判断是否发生了异常
        return e

