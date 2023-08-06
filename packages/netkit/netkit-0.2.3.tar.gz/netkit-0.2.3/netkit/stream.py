# -*- coding: utf-8 -*-

import socket
import functools
import numbers
import collections
import re
from .log import logger


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
    从tornado的iostream衍生而来
    """

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
        self._read_checker = None

        self.reader_count = 0
        self.writer_count = 0

    def close(self, exc_info=False):
        if self.closed():
            # 如果已经关闭过，就直接返回了
            return

        self.close_fd()

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
        try:
            self.sock.shutdown(how)
        finally:
            pass

    @count_reader
    def read_until_regex(self, regex):
        """Run when we read the given regex pattern.
        """
        self._read_regex = re.compile(regex)
        while True:
            ret, data = self._try_inline_read()
            if ret <= 0:
                return data

    @count_reader
    def read_until(self, delimiter):
        """
        为了兼容调用的方法
        """

        self._read_delimiter = delimiter
        while True:
            ret, data = self._try_inline_read()
            if ret <= 0:
                return data

    @count_reader
    def read_bytes(self, num_bytes):
        """Run when we read the given number of bytes.
        """
        assert isinstance(num_bytes, numbers.Integral)
        self._read_bytes = num_bytes
        while True:
            ret, data = self._try_inline_read()
            if ret <= 0:
                return data

    @count_reader
    def read_until_close(self):
        """Reads all data from the socket until it is closed.
        """
        if self.closed():
            return self._consume(self._read_buffer_size)

        self._read_until_close = True
        while True:
            ret, data = self._try_inline_read()
            if ret <= 0:
                return data

    @count_reader
    def read_with_checker(self, checker):
        """
        checker(buf):
            0 继续接收
            >0 使用的长度
            <0 异常
        """

        self._read_checker = checker
        while True:
            ret, data = self._try_inline_read()
            if ret <= 0:
                return data

    @count_writer
    def write(self, data):
        """
        写数据
        """

        if self.closed():
            return -1

        while data:
            try:
                num_bytes = self.write_to_fd(data)
            except:
                logger.error('write fail.', exc_info=True)
                num_bytes = None

            if num_bytes is None:
                return -2

            data = data[num_bytes:]

        return 0

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
            self.sock.setsockopt(
                socket.IPPROTO_TCP, socket.TCP_NODELAY, 1 if value else 0)

    def read_from_fd(self):
        chunk = self.sock.recv(self.read_chunk_size)

        if not chunk:
            self.close()
            return None
        return chunk

    def write_to_fd(self, data):
        return self.sock.send(data)

    def close_fd(self):
        if self.sock:
            try:
                self.sock.close
            finally:
                self.sock = None

    def _try_inline_read(self):
        """Attempt to complete the current read operation from buffered data.

        0 代表获取到数据了；1代表还要继续读；-1代表链接断开
        """
        # See if we've already got the data from a previous read
        data = self._read_from_buffer()
        if data:
            return 0, data

        if self._read_to_buffer() == 0:
            # 说明断连接了
            self.close()

            if self._read_until_close:
                self._read_until_close = False

                return -1, self._consume(self._read_buffer_size)

            # 直接返回，因为buffer里面一定没数据了
            return -1, None

        data = self._read_from_buffer()
        if data:
            # 收到了新的数据，判断下是否满足要求
            return 0, data

        return 1, None

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

        Returns data if the read was completed.
        """
        if self._read_bytes is not None and self._read_buffer_size >= self._read_bytes:
            num_bytes = self._read_bytes
            self._read_bytes = None
            return self._consume(num_bytes)
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
                        delimiter_len = len(self._read_delimiter)
                        self._read_delimiter = None
                        return self._consume(loc + delimiter_len)
                    if len(self._read_buffer) == 1:
                        break
                    _double_prefix(self._read_buffer)
        elif self._read_regex is not None:
            if self._read_buffer:
                while True:
                    m = self._read_regex.search(self._read_buffer[0])
                    if m is not None:
                        self._read_regex = None
                        return self._consume(m.end())
                    if len(self._read_buffer) == 1:
                        break
                    _double_prefix(self._read_buffer)
        elif self._read_checker is not None:
            if self._read_buffer:
                while True:
                    loc, obj = self._read_checker(self._read_buffer[0])
                    if loc > 0:
                        # 说明就是要这些长度
                        self._read_checker = None
                        return self._consume(loc)
                    elif loc < 0:
                        # 说明接受的数据已经有问题了，直接把数据删掉，并退出
                        self._read_buffer.popleft()
                        break

                    if len(self._read_buffer) == 1:
                        break
                    _double_prefix(self._read_buffer)
        return None

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

