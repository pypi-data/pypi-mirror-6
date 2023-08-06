# -*- coding: utf-8 -*-

import struct
from collections import OrderedDict
from .log import logger

# 如果header字段变化，那么格式也会变化
HEADER_ATTRS = OrderedDict([
    ('magic', ('I', 2037952207)),
    ('version', ('I', 0)),
    ('_body_len', ('I', 0)),
    ('cmd', ('i', 0)),
    ('ret', ('i', 0)),
    ('reserve_str', ('32s', ''))
])


class Bintp(object):
    """
    类
    """

    # 如果header字段变化，那么格式也会变化
    header_attrs = None

    _body = ''

    def __init__(self, header_attrs=None):
        self.header_attrs = header_attrs or HEADER_ATTRS

        # 先做初始化
        for k, v in self.header_attrs.items():
            setattr(self, k, v[1])

    @property
    def header_format(self):
        return '!' + ''.join(value[0] for value in self.header_attrs.values())

    @property
    def header_len(self):
        return struct.calcsize(self.header_format)

    @property
    def packet_len(self):
        return self.header_len + self.body_len

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

    def pack(self):
        """
        打包
        """
        values = [getattr(self, k) for k in self.header_attrs]

        header = struct.pack(self.header_format, *values)

        return header + self.body

    def unpack(self, buf):
        """
        从buf里面生成，返回格式为 ret

        >0: 成功生成obj，返回了使用的长度，即剩余的部分buf要存起来
        <0: 报错
        0: 继续收
        """

        if len(buf) < self.header_len:
            logger.error('buf.len(%s) should > header_len(%s)' % (len(buf), self.header_len))
            # raise ValueError('buf.len(%s) should > header_len(%s)' % (len(buf), HEADER_LEN))
            return 0

        try:
            values = struct.unpack(self.header_format, buf[:self.header_len])
        except Exception, e:
            logger.error('unpack fail.', exc_info=True)
            return -1

        dict_values = dict([(key, values[i]) for i, key in enumerate(self.header_attrs.keys())])

        magic = dict_values.get('magic')
        body_len = dict_values.get('_body_len')

        if magic != self.magic:
            logger.error('magic not equal. %s != %s' % (magic, self.magic))
            # raise ValueError('magic not equal. %s != %s' % (magic, HEADER_MAGIC))
            return -2

        if len(buf) < (body_len + self.header_len):
            # 还要继续收
            return 0

        for k, v in dict_values.items():
            setattr(self, k, v)

        self.body = buf[self.header_len:self.header_len+body_len]

        return self.packet_len

    def __repr__(self):
        values = [(k, getattr(self, k)) for k in self.header_attrs]

        values.append(('body', self.body))

        return repr(values)

    __str__ = __repr__
