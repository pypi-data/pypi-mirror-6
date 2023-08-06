# -*- coding: utf-8 -*-

import logging
import msgpack
import socket
import struct
import time
import gsocketpool.connection

MB_SET_BULK = 0xb8
MB_GET_BULK = 0xba
MB_REMOVE_BULK = 0xb9
MB_ERROR = 0xbf
FLAG_NOREPLY = 0x01


class KyotoTycoonError(Exception):
    pass


cdef class KyotoTycoonConnection:
    """Kyoto Tycoon connection.

    Usage:
        >>> from bkyototycoon import KyotoTycoonConnection
        >>> client = KyotoTycoonConnection()
        >>> client.set_bulk({'key1': 'value1', 'key2': 'value2'})
        2
        >>> client.get_bulk(['key1', 'key2', 'key3'])
        {'key2': 'value2', 'key1': 'value1'}
        >>> client.remove_bulk(['key1', 'key2'])
        1
        >>> client.get_bulk(['key1', 'key2', 'key3'])
        {'key1': 'value1'}

    :param str host: (optional) Hostname.
    :param int port: (optional) Port.
    :param float timeout: (optional) Timeout.
    :param bool pack: (optional) If set to True, all values are automatically
        serialized using MessagePack.
    :param bool lazy: (optional) If set to True, the socket connection is not
        established until you specifically call :func:`open() <bkyototycoon.KyotoTycoonConnection.open>`.
    :param str pack_encoding: (optional) The character encoding used to pack
        values using MessagePack.
    :param str unpack_encoding: (optional) The character encoding used to unpack
        values using MessagePack.
    """

    cdef bytes _host
    cdef int _port
    cdef bint _pack
    cdef _timeout
    cdef _socket
    cdef _pack_encoding
    cdef _unpack_encoding

    def __init__(self, host='127.0.0.1', port=1978, timeout=None, pack=True,
                 lazy=False, pack_encoding='utf-8', unpack_encoding='utf-8'):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._pack = pack
        self._pack_encoding = pack_encoding
        self._unpack_encoding = unpack_encoding

        if not lazy:
            self.open()

    def open(self):
        """Opens a connection."""

        assert self._socket is None, 'The connection has already been established'

        logging.debug('Opening a KyotoTycoon connection')

        self._socket = socket.create_connection((self._host, self._port))
        if self._timeout:
            self._socket.settimeout(self._timeout)

    def close(self):
        """Closes the connection."""

        assert self._socket is not None, 'Attempt to close a connection that has not been established'

        logging.debug('Closing a KyotoTycoon connection')

        try:
            self._socket.close()
        except:
            logging.exception('Failed to close the connection')

        self._socket = None

    def is_connected(self):
        """Returns whether the connection has been established."""

        if self._socket:
            return True
        else:
            return False

    def get_bulk(self, list keys):
        """Retreives multiple records at once.

        :param list keys: Cache keys.
        """

        assert self._socket is not None, 'The connection has not been established'

        # create a request
        cdef bytes key, req

        req = b''
        req += struct.pack('!BII', MB_GET_BULK, 0, len(keys))
        for key in keys:
            req += struct.pack('!HI', 0, len(key))
            req += key

        # send the request
        self._socket.sendall(req)

        # parse the response
        cdef int magic, ret_len, key_len, val_len
        cdef dict result = {}

        (magic,) = struct.unpack('!B', self._read(1))
        if magic == MB_GET_BULK:
            (ret_len,) = struct.unpack('!I', self._read(4))

            for _ in xrange(ret_len):
                (_, key_len, val_len, _) = struct.unpack('!HIIq', self._read(18))
                key = self._read(key_len)
                val = self._read(val_len)

                if self._pack:
                    result[key] = msgpack.unpackb(val, encoding=self._unpack_encoding)
                else:
                    result[key] = val

        elif magic == MB_ERROR:
            raise KyotoTycoonError('Internal server error')

        else:
            raise KyotoTycoonError('Unknown server error')

        return result

    def set_bulk(self, dict data, long lifetime=0x7fffffff, bint async=False):
        """Stores multiple records at once.

        :param dict data: Records to be cached.
        :param int lifetime: The number of seconds until the records will expire.
        :param bool async: If set to True, the function immediately returns
            after sending the request.
        """

        assert self._socket is not None, 'The connection has not been established'

        cdef int flags

        if async:
            flags = FLAG_NOREPLY
        else:
            flags = 0

        # create a request
        cdef bytes key
        cdef bytes req

        req = b''
        req += struct.pack('!BII', MB_SET_BULK, flags, len(data))
        for (key, val) in data.iteritems():
            if self._pack:
                val = msgpack.packb(val, encoding=self._pack_encoding)

            req += struct.pack('!HIIq', 0, len(key), len(val), lifetime)
            req += key
            req += val

        self._socket.sendall(req)

        if async:
            return None

        # parse the response
        cdef int magic, rec_len
        cdef dict result = {}

        (magic,) = struct.unpack('!B', self._read(1))
        if magic == MB_SET_BULK:
            (rec_len,) = struct.unpack('!I', self._read(4))
            return rec_len

        elif magic == MB_ERROR:
            raise KyotoTycoonError('Internal server error')

        else:
            raise KyotoTycoonError('Unknown server error')

    def remove_bulk(self, list keys, bint async=False):
        """Removes multiple records at once.

        :param list keys: Cache keys to be removed.
        :param bool async: If set to True, the function immediately returns
            after sending the request.
        """

        assert self._socket is not None, 'The connection has not been established'

        cdef int flags

        if async:
            flags = FLAG_NOREPLY
        else:
            flags = 0

        cdef bytes key
        cdef bytes req

        req = b''
        req += struct.pack('!BII', MB_REMOVE_BULK, flags, len(keys))
        for key in keys:
            req += struct.pack('!HI', 0, len(key))
            req += key

        self._socket.sendall(req)

        if async:
            return None

        # parse the response
        cdef int magic, rec_len
        cdef dict result = {}

        (magic,) = struct.unpack('!B', self._read(1))
        if magic == MB_REMOVE_BULK:
            (rec_len,) = struct.unpack('!I', self._read(4))
            return rec_len

        elif magic == MB_ERROR:
            raise KyotoTycoonError('Internal server error')

        else:
            raise KyotoTycoonError('Unknown server error')

    cdef bytes _read(self, int length):
        cdef int read = 0
        cdef buf = ''
        cdef bytes data

        while read < length:
            data = self._socket.recv(length - read)
            if data:
                buf += data
                read += len(data)
            else:
                raise KyotoTycoonError('Connection closed')

        return buf


class KyotoTycoonPoolConnection(KyotoTycoonConnection, gsocketpool.connection.Connection):
    """Kyoto Tycoon connection wrapper for `gsocketpool <https://github.com/studio-ousia/gsocketpool>`_.

    Usage:
        >>> from bkyototycoon import KyotoTycoonPoolConnection
        >>> from gsocketpool.pool import Pool
        >>> pool = Pool(KyotoTycoonPoolConnection)
        >>> with pool.connection() as conn:
        ...     conn.set_bulk({'key1': 'value1'})
        ...     conn.get_bulk(['key1'])
        1
        {'key1': 'value1'}

    :param str host: (optional) Hostname.
    :param int port: (optional) Port.
    :param float timeout: (optional) Timeout.
    :param bool pack: (optional) If set to True, all values are automatically
        serialized using MessagePack.
    :param str pack_encoding: (optional) The character encoding used to pack
        values using MessagePack.
    :param str unpack_encoding: (optional) The character encoding used to unpack
        values using MessagePack.
    """

    def __init__(self, host='127.0.0.1', port=1978, timeout=None, pack=True,
                 pack_encoding='utf-8', unpack_encoding='utf-8'):
        KyotoTycoonConnection.__init__(
            self, host, port, timeout=timeout, pack=pack, lazy=True,
            pack_encoding=pack_encoding, unpack_encoding=unpack_encoding)


    def get_bulk(self, list keys):
        """Retreives multiple records at once.

        :param list keys: Cache keys.
        """

        try:
            return KyotoTycoonConnection.get_bulk(self, keys)

        except socket.timeout:
            self.reconnect()
            raise

        except IOError:
            self.reconnect()
            raise

    def set_bulk(self, dict data, long lifetime=0x7fffffff, bint async=False):
        """Stores multiple records at once.

        :param dict data: Records to be cached.
        :param int lifetime: The number of seconds until the records will expire.
        :param bool async: If set to True, the function immediately returns
            after sending the request.
        """

        try:
            return KyotoTycoonConnection.set_bulk(self, data, lifetime, async)

        except socket.timeout:
            self.reconnect()
            raise

        except IOError:
            self.reconnect()
            raise

    def remove_bulk(self, list keys, bint async=False):
        """Removes multiple records at once.

        :param list keys: Cache keys to be removed.
        :param bool async: If set to True, the function immediately returns
            after sending the request.
        """

        try:
            return KyotoTycoonConnection.remove_bulk(self, keys, async)

        except socket.timeout:
            self.reconnect()
            raise

        except IOError:
            self.reconnect()
            raise
