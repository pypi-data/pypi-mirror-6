# -*- coding: utf-8 -*-

import struct
from collections import OrderedDict
from .log import logger


HEADER_MAGIC = 2037952207

# 如果header字段变化，那么格式也会变化
HEADER_ATTRS = OrderedDict([
    ('magic', ('I', HEADER_MAGIC)),
    ('version', ('I', 0)),
    ('_body_len', ('I', 0)),
    ('cmd', ('i', 0)),
    ('ret', ('i', 0)),
    ('reserve_uint1', ('I', 0)),
    ('reserve_uint2', ('I', 0)),
    ('reserve_uint3', ('I', 0)),
    ('reserve_uint4', ('I', 0)),
    ('reserve_int1', ('i', 0)),
    ('reserve_int2', ('i', 0)),
    ('reserve_int3', ('i', 0)),
    ('reserve_int4', ('i', 0)),
    ('reserve_str', ('32s', ''))
])

HEADER_FORMAT = '!' + ''.join(value[0] for value in HEADER_ATTRS.values())
HEADER_LEN = struct.calcsize(HEADER_FORMAT)


class Bintp(object):
    """
    类
    """

    _body = ''

    def __init__(self):
        # 先做初始化
        for k, v in HEADER_ATTRS.items():
            setattr(self, k, v[1])

    def pack(self):
        """
        打包
        """
        values = [getattr(self, k) for k in HEADER_ATTRS]

        header = struct.pack(HEADER_FORMAT, *values)

        return header + self.body

    @property
    def header_len(self):
        return HEADER_LEN

    @property
    def packet_len(self):
        return HEADER_LEN + self.body_len

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

        return repr(values)

    __str__ = __repr__


def new():
    return Bintp()


def check_buf(buf):
    """
    检查buf是否合法
    >0: 成功，返回了使用的长度
    <0: 报错
    0: 继续收
    """
    return _inline_from_buf(buf)[0]


def from_buf(buf):
    """
    返回生成的tp
    None: 生成失败
    非None: 生成成功
    """
    return _inline_from_buf(buf)[1]


def _inline_from_buf(buf):
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

    dict_values = dict([(key, values[i]) for i, key in enumerate(HEADER_ATTRS.keys())])

    magic = dict_values.get('magic')
    body_len = dict_values.get('_body_len')

    if magic != HEADER_MAGIC:
        logger.error('magic not equal. %s != %s' % (magic, HEADER_MAGIC))
        # raise ValueError('magic not equal. %s != %s' % (magic, HEADER_MAGIC))
        return -2, None

    if len(buf) < (body_len + HEADER_LEN):
        # 还要继续收
        return 0, None

    tp = Bintp()

    for k, v in dict_values.items():
        setattr(tp, k, v)

    tp.body = buf[HEADER_LEN:HEADER_LEN+body_len]

    return tp.packet_len, tp
