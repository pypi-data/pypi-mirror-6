# -*- coding: utf-8 -*-
"""
#=============================================================================
#
#     FileName: stream.py
#         Desc: stream for network. can use with normal socket or gevent socket.
#
#       Author: dantezhu
#        Email: zny2008@gmail.com
#     HomePage: http://www.vimer.cn
#
#      Created: 2014-04-22 18:33:20
#      Version: 0.0.1
#      History:
#               0.0.1 | dantezhu | 2014-04-22 18:33:20 | init
#
#=============================================================================
"""

import socket
import functools
import numbers
import collections
import re
from .log import logger
from .utils import safe_call


def count_reader(func):
    @functools.wraps(func)
    def func_wrapper(stream, *args, **kwargs):
        try:
            stream.reader_count += 1
            return func(stream, *args, **kwargs)
        finally:
            stream.reader_count -= 1

    return func_wrapper


def count_writer(func):
    @functools.wraps(func)
    def func_wrapper(stream, *args, **kwargs):
        try:
            stream.writer_count += 1
            return func(stream, *args, **kwargs)
        finally:
            stream.writer_count -= 1
    return func_wrapper


class Stream(object):
    """
    为了和tornado的IOStream接口匹配
    """

    _close_callback = None

    def __init__(self, sock, max_buffer_size=None,
                 read_chunk_size=4096):
        self.sock = sock
        self.max_buffer_size = max_buffer_size or 104857600
        self.read_chunk_size = read_chunk_size

        self._read_buffer = collections.deque()
        self._read_buffer_size = 0
        self._read_delimiter = None
        self._read_regex = None
        self._read_bytes = None
        self._read_until_close = False
        self._read_callback = None
        self._streaming_callback = None
        self._read_checker = None
        self._close_callback = None

        self.reader_count = 0
        self.writer_count = 0

    def close(self, exc_info=False):
        if self.closed():
            # 如果已经关闭过，就直接返回了
            return

        if self.sock:
            safe_call(self.sock.close)
            self.sock = None

    def shutdown(self, how=2):
        """
        gevent的close只是把sock替换为另一个类的实例。
        这个实例的任何方法都会报错，但只有当真正调用recv、write或者有recv or send事件的时候，才会调用到这些函数，才可能检测到。
        而我们在endpoint对应的函数里spawn_later一个新greenlet而不做join的话，connection的while循环此时已经开始read了。

        之所以不把这个函数实现到connection，是因为shutdown更类似于触发一个close的事件
        用shutdown可以直接触发. how: 0: SHUT_RD, 1: SHUT_WR, else: all
        shutdown后还是会触发close事件以及相关的回调函数，不必担心
        """
        if self.closed():
            return
        safe_call(self.sock.shutdown, how)

    def set_close_callback(self, callback):
        """
        设置回调
        """
        self._close_callback = callback

    @count_reader
    def read_until_regex(self, regex, callback):
        """Run ``callback`` when we read the given regex pattern.

        The callback will get the data read (including the data that
        matched the regex and anything that came before it) as an argument.
        """
        self._set_read_callback(callback)
        self._read_regex = re.compile(regex)
        while True:
            # 0 代表调用到callback；1代表还要继续读；-1代表链接断开
            if self._try_inline_read() <= 0:
                break

    @count_reader
    def read_until(self, delimiter, callback):
        """
        为了兼容调用的方法
        """

        self._set_read_callback(callback)
        self._read_delimiter = delimiter
        while True:
            # 0 代表调用到callback；1代表还要继续读；-1代表链接断开
            if self._try_inline_read() <= 0:
                break

    @count_reader
    def read_bytes(self, num_bytes, callback, streaming_callback=None):
        """Run callback when we read the given number of bytes.

        If a ``streaming_callback`` is given, it will be called with chunks
        of data as they become available, and the argument to the final
        ``callback`` will be empty.  Otherwise, the ``callback`` gets
        the data as an argument.
        """
        self._set_read_callback(callback)
        assert isinstance(num_bytes, numbers.Integral)
        self._read_bytes = num_bytes
        self._streaming_callback = streaming_callback
        while True:
            # 0 代表调用到callback；1代表还要继续读；-1代表链接断开
            if self._try_inline_read() <= 0:
                break

    @count_reader
    def read_until_close(self, callback, streaming_callback=None):
        """Reads all data from the socket until it is closed.

        If a ``streaming_callback`` is given, it will be called with chunks
        of data as they become available, and the argument to the final
        ``callback`` will be empty.  Otherwise, the ``callback`` gets the
        data as an argument.

        Subject to ``max_buffer_size`` limit from `IOStream` constructor if
        a ``streaming_callback`` is not used.
        """
        self._set_read_callback(callback)
        self._streaming_callback = streaming_callback
        if self.closed():
            if self._streaming_callback is not None:
                self._run_callback(self._streaming_callback,
                                   self._consume(self._read_buffer_size))
            self._run_callback(self._read_callback,
                               self._consume(self._read_buffer_size))
            self._streaming_callback = None
            self._read_callback = None
            return

        self._read_until_close = True
        self._streaming_callback = streaming_callback
        while True:
            # 0 代表调用到callback；1代表还要继续读；-1代表链接断开
            if self._try_inline_read() < 0:
                break

    @count_reader
    def read_with_checker(self, checker, callback):
        """
        checker(buf):
            0 继续接收
            >0 使用的长度
            <0 异常
        """

        self._set_read_callback(callback)
        self._read_checker = checker
        while True:
            # 0 代表调用到callback；1代表还要继续读；-1代表链接断开
            if self._try_inline_read() <= 0:
                break

    @count_writer
    def write(self, data, callback=None):
        """
        写数据
        """

        if self.closed():
            return

        while data:
            num_bytes = safe_call(self.write_to_fd, data)
            if num_bytes is None:
                logger.error('write num_bytes: %s', num_bytes)
                break

            data = data[num_bytes:]

        if callback:
            self._run_callback(callback)

    def closed(self):
        return not self.sock

    def reading(self):
        return bool(self.reader_count)

    def writing(self):
        return bool(self.writer_count)

    def set_nodelay(self, value):
        """
        直接抄的tornado
        """
        if (self.sock is not None and
                    self.sock.family in (socket.AF_INET, socket.AF_INET6)):
            safe_call(self.sock.setsockopt,
                      socket.IPPROTO_TCP, socket.TCP_NODELAY, 1 if value else 0)

    def read_from_fd(self):
        return self.sock.recv(self.read_chunk_size)

    def write_to_fd(self, data):
        return self.sock.send(data)

    def _run_callback(self, callback, *args):
        """
        替换为kola的safe_call
        """
        return safe_call(callback, *args)

    def _set_read_callback(self, callback):
        assert not self._read_callback, "Already reading"
        self._read_callback = callback

    def _try_inline_read(self):
        """Attempt to complete the current read operation from buffered data.

        If the read can be completed without blocking, schedules the
        read callback on the next IOLoop iteration; otherwise starts
        listening for reads on the socket.
        """
        # See if we've already got the data from a previous read
        if self._read_from_buffer():
            return 0

        if self._read_to_buffer() == 0:
            # 说明断连接了
            self.close()

            if self._read_until_close:
                if (self._streaming_callback is not None and
                        self._read_buffer_size):
                    self._run_callback(self._streaming_callback,
                                       self._consume(self._read_buffer_size))
                callback = self._read_callback
                self._read_callback = None
                self._read_until_close = False
                self._run_callback(callback,
                                   self._consume(self._read_buffer_size))

            if self._close_callback:
                self._run_callback(self._close_callback)
                self._close_callback = None

            # 直接返回，因为buffer里面一定没数据了
            return -1

        if self._read_from_buffer():
            # 收到了新的数据，判断下是否满足要求
            return 0

        return 1

    def _read_to_buffer(self):
        """Reads from the socket and appends the result to the read buffer.

        Returns the number of bytes read.  Returns 0 if there is nothing
        to read (i.e. the read returns EWOULDBLOCK or equivalent).  On
        error closes the socket and raises an exception.
        """
        chunk = self.read_from_fd()

        if chunk is None:
            return 0

        self._read_buffer.append(chunk)
        self._read_buffer_size += len(chunk)
        if self._read_buffer_size >= self.max_buffer_size:
            logger.error("Reached maximum read buffer size")
            self.close()
            raise IOError("Reached maximum read buffer size")
        return len(chunk)

    def _read_from_buffer(self):
        """Attempts to complete the currently-pending read from the buffer.

        Returns True if the read was completed.
        """
        if self._streaming_callback is not None and self._read_buffer_size:
            bytes_to_consume = self._read_buffer_size
            if self._read_bytes is not None:
                bytes_to_consume = min(self._read_bytes, bytes_to_consume)
                self._read_bytes -= bytes_to_consume
            self._run_callback(self._streaming_callback,
                               self._consume(bytes_to_consume))
        if self._read_bytes is not None and self._read_buffer_size >= self._read_bytes:
            num_bytes = self._read_bytes
            callback = self._read_callback
            self._read_callback = None
            self._streaming_callback = None
            self._read_bytes = None
            self._run_callback(callback, self._consume(num_bytes))
            return True
        elif self._read_delimiter is not None:
            # Multi-byte delimiters (e.g. '\r\n') may straddle two
            # chunks in the read buffer, so we can't easily find them
            # without collapsing the buffer.  However, since protocols
            # using delimited reads (as opposed to reads of a known
            # length) tend to be "line" oriented, the delimiter is likely
            # to be in the first few chunks.  Merge the buffer gradually
            # since large merges are relatively expensive and get undone in
            # consume().
            if self._read_buffer:
                while True:
                    loc = self._read_buffer[0].find(self._read_delimiter)
                    if loc != -1:
                        callback = self._read_callback
                        delimiter_len = len(self._read_delimiter)
                        self._read_callback = None
                        self._streaming_callback = None
                        self._read_delimiter = None
                        self._run_callback(callback,
                                           self._consume(loc + delimiter_len))
                        return True
                    if len(self._read_buffer) == 1:
                        break
                    _double_prefix(self._read_buffer)
        elif self._read_regex is not None:
            if self._read_buffer:
                while True:
                    m = self._read_regex.search(self._read_buffer[0])
                    if m is not None:
                        callback = self._read_callback
                        self._read_callback = None
                        self._streaming_callback = None
                        self._read_regex = None
                        self._run_callback(callback, self._consume(m.end()))
                        return True
                    if len(self._read_buffer) == 1:
                        break
                    _double_prefix(self._read_buffer)
        elif self._read_checker is not None:
            if self._read_buffer:
                while True:
                    loc, obj = self._read_checker(self._read_buffer[0])
                    if loc > 0:
                        # 说明就是要这些长度
                        callback = self._read_callback
                        self._read_callback = None
                        self._streaming_callback = None
                        self._read_delimiter = None
                        self._run_callback(callback,
                                           self._consume(loc))
                        return True
                    elif loc < 0:
                        # 说明接受的数据已经有问题了，直接把数据删掉，并退出
                        self._read_buffer.popleft()
                        break

                    if len(self._read_buffer) == 1:
                        break
                    _double_prefix(self._read_buffer)
        return False

    def _consume(self, loc):
        if loc == 0:
            return b""
        _merge_prefix(self._read_buffer, loc)
        self._read_buffer_size -= loc
        return self._read_buffer.popleft()


def _double_prefix(deque):
    """Grow by doubling, but don't split the second chunk just because the
    first one is small.
    """
    new_len = max(len(deque[0]) * 2,
                  (len(deque[0]) + len(deque[1])))
    _merge_prefix(deque, new_len)


def _merge_prefix(deque, size):
    """Replace the first entries in a deque of strings with a single
    string of up to size bytes.

    >>> d = collections.deque(['abc', 'de', 'fghi', 'j'])
    >>> _merge_prefix(d, 5); print(d)
    deque(['abcde', 'fghi', 'j'])

    Strings will be split as necessary to reach the desired size.
    >>> _merge_prefix(d, 7); print(d)
    deque(['abcdefg', 'hi', 'j'])

    >>> _merge_prefix(d, 3); print(d)
    deque(['abc', 'defg', 'hi', 'j'])

    >>> _merge_prefix(d, 100); print(d)
    deque(['abcdefghij'])
    """
    if len(deque) == 1 and len(deque[0]) <= size:
        return
    prefix = []
    remaining = size
    while deque and remaining > 0:
        chunk = deque.popleft()
        if len(chunk) > remaining:
            deque.appendleft(chunk[remaining:])
            chunk = chunk[:remaining]
        prefix.append(chunk)
        remaining -= len(chunk)
    # This data structure normally just contains byte strings, but
    # the unittest gets messy if it doesn't use the default str() type,
    # so do the merge based on the type of data that's actually present.
    if prefix:
        deque.appendleft(type(prefix[0])().join(prefix))
    if not deque:
        deque.appendleft(b"")


def doctests():
    import doctest
    return doctest.DocTestSuite()

