# -*- coding: utf-8 -*-

import struct
from collections import OrderedDict
from .log import logger


HEADER_MAGIC = 2037952207

# 如果header字段变化，那么格式也要变化
HEADER_FORMAT = '!3I2i4I4i32s'
HEADER_LEN = struct.calcsize(HEADER_FORMAT)

HEADER_ATTRS = OrderedDict([
    ('_magic', HEADER_MAGIC),   # unsigned int
    ('version', 0),  # unsigned int
    ('_body_len', 0),  # unsigned int
    ('cmd', 0),  # int
    ('ret', 0),  # int
    ('reserve_uint1', 0),
    ('reserve_uint2', 0),
    ('reserve_uint3', 0),
    ('reserve_uint4', 0),
    ('reserve_int1', 0),
    ('reserve_int2', 0),
    ('reserve_int3', 0),
    ('reserve_int4', 0),
    ('reserve_str', '\0' * 32)
])


def new():
    return Bintp()


def from_buf(buf):
    """
    从buf里面生成，返回格式为 ret, obj

    >0: 成功生成obj，返回了使用的长度，即剩余的部分buf要存起来
    <0: 报错
    0: 继续收

    """

    if len(buf) < HEADER_LEN:
        logger.error('buf.len(%s) should > header_len(%s)' % (len(buf), HEADER_LEN))
        # raise ValueError('buf.len(%s) should > header_len(%s)' % (len(buf), HEADER_LEN))
        return 0, None

    try:
        values = struct.unpack(HEADER_FORMAT, buf[:HEADER_LEN])
    except Exception, e:
        logger.error('unpack fail.', exc_info=True)
        return -1, None

    magic = values[0]
    body_len = values[2]

    if magic != HEADER_MAGIC:
        logger.error('magic not equal. %s != %s' % (magic, HEADER_MAGIC))
        # raise ValueError('magic not equal. %s != %s' % (magic, HEADER_MAGIC))
        return -2, None

    if len(buf) < (body_len + HEADER_LEN):
        # 还要继续收
        return 0, None

    tp = Bintp()

    for i, k in enumerate(HEADER_ATTRS.keys()):
        setattr(tp, k, values[i])

    tp.body = buf[HEADER_LEN:HEADER_LEN+body_len]

    return tp.packet_len, tp


class Bintp(object):
    """
    类
    """

    _body = ''

    def __init__(self):
        # 先做初始化
        for k, v in HEADER_ATTRS.items():
            setattr(self, k, v)

    def pack(self):
        """
        打包
        """
        values = [getattr(self, k) for k in HEADER_ATTRS]

        header = struct.pack(HEADER_FORMAT, *values)

        return header + self.body

    @property
    def packet_len(self):
        return HEADER_LEN + self.body_len

    @property
    def magic(self):
        return self._magic

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = value
        self._body_len = len(self._body)

    @property
    def body_len(self):
        return self._body_len

    def __repr__(self):
        values = [(k, getattr(self, k)) for k in HEADER_ATTRS]

        values.append(('body', self.body))

        return str(values)

    __unicode__ = __str__ = __repr__
