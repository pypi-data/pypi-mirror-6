#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
acidfile module just provide an object, the ACIDFile object. This object
can be used as a regular file object but instead of write one copy of the data,
it will write several copies to disk in an ACID manner.

The original algorithm was borrowed from this blog post authored by
Elvis Pfützenreuter:

http://epx.com.br/artigos/arqtrans_en.php
"""

from time import time
import hmac
import os
import struct
import sys

if sys.version_info.major == 2:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
elif sys.version_info.major == 3:
    from io import BytesIO as StringIO

class ACIDFile(object):
    """
    A file-like object with ACID features.

    Data will be stored in memory until the file is closed. Then two copies of
    the data will be written to several files with an timestamp and a HMAC.

    When the file is readed the most recent and correct copy of the data will
    be retrieved.
    """
    _mac_size = 16
    _timestamp_size = 8
    def __init__(self, name, mode='r', key=b'ACIDFILE', copies=1,
                 *args, **kwargs):

        if copies < 1:
            raise ValueError('copies must be greater than 0')

        self._filenames = []
        self.key = key

        self.copies = copies
        for idx in range(self.copies + 1):
            self._filenames.append('{prefix}.{idx}'.format(
                prefix=name,
                idx=idx))
        self._file = StringIO()
        self.loaded = 'w' in mode

    def read(self, size=-1):
        """
        If the data is on disk, read the data from the most recent valid file.
        If the data is in memory return it.
        """
        if not self.loaded:
            timestamps = list()
            for subfile in self._filenames:
                if os.path.exists(subfile):
                    with open(subfile, 'rb') as f:
                        f.seek(self._mac_size)
                        timestamp = struct.unpack('d',
                                                  f.read(self._timestamp_size))
                        timestamps.append((timestamp[0], subfile))

            for _, subfile in sorted(timestamps, reverse=True):
                if os.path.exists(subfile):
                    with open(subfile, 'rb') as f:
                        file_signature = f.read(self._mac_size)
                        content = f.read()
                        actual_signature = hmac.new(self.key, content).digest()
                        if actual_signature == file_signature:
                            self._file.write(content[self._timestamp_size:])
                            self._file.seek(0)
                            self.loaded = True
                            break
                        else:
                            continue
            if not self.loaded:
                raise IOError("Can't read file")
        return self._file.read(size)

    def write(self, str):
        """
        Write data to memory.
        """
        return self._file.write(str)

    def close(self):
        """
        Commit the memory data to disk.
        """
        if self.loaded:
            self._file.seek(0)
            raw_content = self._file.read()
            for subfile in self._filenames:
                now = time()
                timestamp = struct.pack('d', now)
                content = timestamp + raw_content
                signature = hmac.new(self.key, content).digest()
                with open(subfile, 'wb') as f:
                    f.write(signature)
                    f.write(content)
                    f.flush()
                    os.fsync(f.fileno())
        self._file.close()

    def __enter__(self):
        """
        Return self as context.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close and commit data.
        """
        self.close()

    def __getattr__(self, attr):
        """
        If the method is not present call the inner memory file method.
        """
        return getattr(self._file, attr)
