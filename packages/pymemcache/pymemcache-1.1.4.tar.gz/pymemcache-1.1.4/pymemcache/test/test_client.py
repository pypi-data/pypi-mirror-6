# Copyright 2012 Pinterest.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import json
import socket
import unittest

from nose import tools
from pymemcache.client import Client, MemcacheUnknownCommandError
from pymemcache.client import MemcacheClientError, MemcacheServerError
from pymemcache.client import MemcacheUnknownError, MemcacheIllegalInputError
from pymemcache.test.utils import MockMemcacheClient


class MockSocket(object):
    def __init__(self, recv_bufs):
        self.recv_bufs = collections.deque(recv_bufs)
        self.send_bufs = []
        self.closed = False
        self.timeouts = []
        self.connections = []
        self.socket_options = []

    def sendall(self, value):
        self.send_bufs.append(value)

    def close(self):
        self.closed = True

    def recv(self, size):
        value = self.recv_bufs.popleft()
        if isinstance(value, Exception):
            raise value
        return value

    def settimeout(self, timeout):
        self.timeouts.append(timeout)

    def connect(self, server):
        self.connections.append(server)

    def setsockopt(self, level, option, value):
        self.socket_options.append((level, option, value))


class MockSocketModule(object):
    def socket(self, family, type):
        return MockSocket([])

    def __getattr__(self, name):
        return getattr(socket, name)


class ClientTestMixin(object):
    def test_set_success(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r\n'])
        result = client.set('key', 'value', noreply=False)
        tools.assert_equal(result, True)

    def test_set_unicode_key(self):
        client = self.Client(None)
        client.sock = MockSocket([''])

        def _set():
            client.set(u'\u0FFF', 'value', noreply=False)

        tools.assert_raises(MemcacheIllegalInputError, _set)

    def test_set_unicode_value(self):
        client = self.Client(None)
        client.sock = MockSocket([''])

        def _set():
            client.set('key', u'\u0FFF', noreply=False)

        tools.assert_raises(MemcacheIllegalInputError, _set)

    def test_set_noreply(self):
        client = self.Client(None)
        client.sock = MockSocket([])
        result = client.set('key', 'value', noreply=True)
        tools.assert_equal(result, True)

    def test_set_many_success(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r\n'])
        result = client.set_many({'key' : 'value'}, noreply=False)
        tools.assert_equal(result, True)

    def test_add_stored(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r', '\n'])
        result = client.add('key', 'value', noreply=False)
        tools.assert_equal(result, True)

    def test_add_not_stored(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r', '\n'])
        result = client.add('key', 'value', noreply=False)

        client.sock = MockSocket(['NOT_', 'STOR', 'ED', '\r\n'])
        result = client.add('key', 'value', noreply=False)
        tools.assert_equal(result, False)

    def test_get_not_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['END\r\n'])
        result = client.get('key')
        tools.assert_equal(result, None)

    def test_get_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r\n'])
        result = client.set('key', 'value', noreply=False)

        client.sock = MockSocket(['VALUE key 0 5\r\nvalue\r\nEND\r\n'])
        result = client.get('key')
        tools.assert_equal(result, 'value')

    def test_get_many_none_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['END\r\n'])
        result = client.get_many(['key1', 'key2'])
        tools.assert_equal(result, {})

    def test_get_many_some_found(self):
        client = self.Client(None)

        client.sock = MockSocket(['STORED\r\n'])
        result = client.set('key1', 'value1', noreply=False)

        client.sock = MockSocket(['VALUE key1 0 6\r\nvalue1\r\nEND\r\n'])
        result = client.get_many(['key1', 'key2'])
        tools.assert_equal(result, {'key1': 'value1'})

    def test_get_many_all_found(self):
        client = self.Client(None)

        client.sock = MockSocket(['STORED\r\n'])
        result = client.set('key1', 'value1', noreply=False)

        client.sock = MockSocket(['STORED\r\n'])
        result = client.set('key2', 'value2', noreply=False)

        client.sock = MockSocket(['VALUE key1 0 6\r\nvalue1\r\n'
                                'VALUE key2 0 6\r\nvalue2\r\nEND\r\n'])
        result = client.get_many(['key1', 'key2'])
        tools.assert_equal(result, {'key1': 'value1', 'key2': 'value2'})

    def test_get_unicode_key(self):
        client = self.Client(None)
        client.sock = MockSocket([''])

        def _get():
            client.get(u'\u0FFF')

        tools.assert_raises(MemcacheIllegalInputError, _get)

    def test_delete_not_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['NOT_FOUND\r\n'])
        result = client.delete('key', noreply=False)
        tools.assert_equal(result, False)

    def test_delete_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r', '\n'])
        result = client.add('key', 'value', noreply=False)

        client.sock = MockSocket(['DELETED\r\n'])
        result = client.delete('key', noreply=False)
        tools.assert_equal(result, True)

    def test_delete_noreply(self):
        client = self.Client(None)
        client.sock = MockSocket([])
        result = client.delete('key', noreply=True)
        tools.assert_equal(result, True)

    def test_incr_not_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['NOT_FOUND\r\n'])
        result = client.incr('key', 1, noreply=False)
        tools.assert_equal(result, None)

    def test_incr_found(self):
        client = self.Client(None)

        client.sock = MockSocket(['STORED\r\n'])
        client.set('key', 0, noreply=False)

        client.sock = MockSocket(['1\r\n'])
        result = client.incr('key', 1, noreply=False)
        tools.assert_equal(result, 1)

    def test_incr_noreply(self):
        client = self.Client(None)

        client.sock = MockSocket(['STORED\r\n'])
        client.set('key', 0, noreply=False)

        client.sock = MockSocket([])
        result = client.incr('key', 1, noreply=True)
        tools.assert_equal(result, None)

    def test_decr_not_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['NOT_FOUND\r\n'])
        result = client.decr('key', 1, noreply=False)
        tools.assert_equal(result, None)

    def test_decr_found(self):
        client = self.Client(None)

        client.sock = MockSocket(['STORED\r\n'])
        client.set('key', 2, noreply=False)

        client.sock = MockSocket(['1\r\n'])
        result = client.decr('key', 1, noreply=False)
        tools.assert_equal(result, 1)


class TestClient(ClientTestMixin, unittest.TestCase):

    Client = Client

    def test_append_stored(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r\n'])
        result = client.append('key', 'value', noreply=False)
        tools.assert_equal(result, True)

    def test_prepend_stored(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r\n'])
        result = client.prepend('key', 'value', noreply=False)
        tools.assert_equal(result, True)

    def test_cas_stored(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r\n'])
        result = client.cas('key', 'value', 'cas', noreply=False)
        tools.assert_equal(result, True)

    def test_cas_exists(self):
        client = self.Client(None)
        client.sock = MockSocket(['EXISTS\r\n'])
        result = client.cas('key', 'value', 'cas', noreply=False)
        tools.assert_equal(result, False)

    def test_cas_not_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['NOT_FOUND\r\n'])
        result = client.cas('key', 'value', 'cas', noreply=False)
        tools.assert_equal(result, None)

    def test_cr_nl_boundaries(self):
        client = self.Client(None)
        client.sock = MockSocket(['VALUE key1 0 6\r',
                                '\nvalue1\r\n'
                                'VALUE key2 0 6\r\n',
                                'value2\r\n'
                                'END\r\n'])
        result = client.get_many(['key1', 'key2'])
        tools.assert_equals(result, {'key1': 'value1', 'key2': 'value2'})

        client.sock = MockSocket(['VALUE key1 0 6\r\n',
                                'value1\r',
                                '\nVALUE key2 0 6\r\n',
                                'value2\r\n',
                                'END\r\n'])
        result = client.get_many(['key1', 'key2'])
        tools.assert_equals(result, {'key1': 'value1', 'key2': 'value2'})

        client.sock = MockSocket(['VALUE key1 0 6\r\n',
                                'value1\r\n',
                                'VALUE key2 0 6\r',
                                '\nvalue2\r\n',
                                'END\r\n'])
        result = client.get_many(['key1', 'key2'])
        tools.assert_equals(result, {'key1': 'value1', 'key2': 'value2'})


        client.sock = MockSocket(['VALUE key1 0 6\r\n',
                                'value1\r\n',
                                'VALUE key2 0 6\r\n',
                                'value2\r',
                                '\nEND\r\n'])
        result = client.get_many(['key1', 'key2'])
        tools.assert_equals(result, {'key1': 'value1', 'key2': 'value2'})

        client.sock = MockSocket(['VALUE key1 0 6\r\n',
                                'value1\r\n',
                                'VALUE key2 0 6\r\n',
                                'value2\r\n',
                                'END\r',
                                '\n'])
        result = client.get_many(['key1', 'key2'])
        tools.assert_equals(result, {'key1': 'value1', 'key2': 'value2'})

        client.sock = MockSocket(['VALUE key1 0 6\r',
                                '\nvalue1\r',
                                '\nVALUE key2 0 6\r',
                                '\nvalue2\r',
                                '\nEND\r',
                                '\n'])
        result = client.get_many(['key1', 'key2'])
        tools.assert_equals(result, {'key1': 'value1', 'key2': 'value2'})

    def test_delete_exception(self):
        client = self.Client(None)
        client.sock = MockSocket([Exception('fail')])

        def _delete():
            client.delete('key', noreply=False)

        tools.assert_raises(Exception, _delete)
        tools.assert_equal(client.sock, None)
        tools.assert_equal(client.buf, '')

    def test_flush_all(self):
        client = self.Client(None)
        client.sock = MockSocket(['OK\r\n'])
        result = client.flush_all(noreply=False)
        tools.assert_equal(result, True)

    def test_incr_exception(self):
        client = self.Client(None)
        client.sock = MockSocket([Exception('fail')])

        def _incr():
            client.incr('key', 1)

        tools.assert_raises(Exception, _incr)
        tools.assert_equal(client.sock, None)
        tools.assert_equal(client.buf, '')

    def test_get_error(self):
        client = self.Client(None)
        client.sock = MockSocket(['ERROR\r\n'])

        def _get():
            client.get('key')

        tools.assert_raises(MemcacheUnknownCommandError, _get)

    def test_get_recv_chunks(self):
        client = self.Client(None)
        client.sock = MockSocket(['VALUE key', ' 0 5\r', '\nvalue', '\r\n',
                                'END', '\r', '\n'])
        result = client.get('key')
        tools.assert_equal(result, 'value')

    def test_get_unknown_error(self):
        client = self.Client(None)
        client.sock = MockSocket(['foobarbaz\r\n'])

        def _get():
            client.get('key')

        tools.assert_raises(MemcacheUnknownError, _get)

    def test_gets_not_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['END\r\n'])
        result = client.gets('key')
        tools.assert_equal(result, (None, None))

    def test_gets_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['VALUE key 0 5 10\r\nvalue\r\nEND\r\n'])
        result = client.gets('key')
        tools.assert_equal(result, ('value', '10'))

    def test_gets_many_none_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['END\r\n'])
        result = client.gets_many(['key1', 'key2'])
        tools.assert_equal(result, {})

    def test_gets_many_some_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['VALUE key1 0 6 11\r\nvalue1\r\nEND\r\n'])
        result = client.gets_many(['key1', 'key2'])
        tools.assert_equal(result, {'key1': ('value1', '11')})

    def test_touch_not_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['NOT_FOUND\r\n'])
        result = client.touch('key', noreply=False)
        tools.assert_equal(result, False)

    def test_touch_found(self):
        client = self.Client(None)
        client.sock = MockSocket(['TOUCHED\r\n'])
        result = client.touch('key', noreply=False)
        tools.assert_equal(result, True)

    def test_quit(self):
        client = self.Client(None)
        client.sock = MockSocket([])
        result = client.quit()
        tools.assert_equal(result, None)
        tools.assert_equal(client.sock, None)
        tools.assert_equal(client.buf, '')

    def test_replace_stored(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r\n'])
        result = client.replace('key', 'value', noreply=False)
        tools.assert_equal(result, True)

    def test_replace_not_stored(self):
        client = self.Client(None)
        client.sock = MockSocket(['NOT_STORED\r\n'])
        result = client.replace('key', 'value', noreply=False)
        tools.assert_equal(result, False)

    def test_serialization(self):
        def _ser(key, value):
            return json.dumps(value), 0

        client = self.Client(None, serializer=_ser)
        client.sock = MockSocket(['STORED\r\n'])
        client.set('key', {'a': 'b', 'c': 'd'})
        tools.assert_equal(client.sock.send_bufs, [
            'set key 0 0 20 noreply\r\n{"a": "b", "c": "d"}\r\n'
        ])

    def test_set_socket_handling(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r\n'])
        result = client.set('key', 'value', noreply=False)
        tools.assert_equal(result, True)
        tools.assert_equal(client.sock.closed, False)
        tools.assert_equal(len(client.sock.send_bufs), 1)

    def test_set_error(self):
        client = self.Client(None)
        client.sock = MockSocket(['ERROR\r\n'])

        def _set():
            client.set('key', 'value', noreply=False)

        tools.assert_raises(MemcacheUnknownCommandError, _set)

    def test_set_exception(self):
        client = self.Client(None)
        client.sock = MockSocket([Exception('fail')])

        def _set():
            client.set('key', 'value', noreply=False)

        tools.assert_raises(Exception, _set)
        tools.assert_equal(client.sock, None)
        tools.assert_equal(client.buf, '')

    def test_set_client_error(self):
        client = self.Client(None)
        client.sock = MockSocket(['CLIENT_ERROR some message\r\n'])

        def _set():
            client.set('key', 'value', noreply=False)

        tools.assert_raises(MemcacheClientError, _set)

    def test_set_server_error(self):
        client = self.Client(None)
        client.sock = MockSocket(['SERVER_ERROR some message\r\n'])

        def _set():
            client.set('key', 'value', noreply=False)

        tools.assert_raises(MemcacheServerError, _set)

    def test_set_unknown_error(self):
        client = self.Client(None)
        client.sock = MockSocket(['foobarbaz\r\n'])

        def _set():
            client.set('key', 'value', noreply=False)

        tools.assert_raises(MemcacheUnknownError, _set)

    def test_set_many_socket_handling(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r\n'])
        result = client.set_many({'key' : 'value'}, noreply=False)
        tools.assert_equal(result, True)
        tools.assert_equal(client.sock.closed, False)
        tools.assert_equal(len(client.sock.send_bufs), 1)

    def test_set_many_exception(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r\n', Exception('fail')])

        def _set():
            client.set_many({'key' : 'value', 'other' : 'value'}, noreply=False)

        tools.assert_raises(Exception, _set)
        tools.assert_equal(client.sock, None)
        tools.assert_equal(client.buf, '')

    def test_stats(self):
        client = self.Client(None)
        client.sock = MockSocket(['STAT fake_stats 1\r\n', 'END\r\n'])
        result = client.stats()
        tools.assert_equal(client.sock.send_bufs, [
            'stats \r\n'
        ])
        tools.assert_equal(result, {'fake_stats': 1})

    def test_stats_with_args(self):
        client = self.Client(None)
        client.sock = MockSocket(['STAT fake_stats 1\r\n', 'END\r\n'])
        result = client.stats('some_arg')
        tools.assert_equal(client.sock.send_bufs, [
            'stats some_arg\r\n'
        ])
        tools.assert_equal(result, {'fake_stats': 1})

    def test_stats_conversions(self):
        client = self.Client(None)
        client.sock = MockSocket([
            # Most stats are converted to int
            'STAT cmd_get 2519\r\n',
            'STAT cmd_set 3099\r\n',

            # Unless they can't be, they remain str
            'STAT libevent 2.0.19-stable\r\n',

            # Some named stats are explicitly converted
            'STAT hash_is_expanding 0\r\n',
            'STAT rusage_user 0.609165\r\n',
            'STAT rusage_system 0.852791\r\n',
            'STAT slab_reassign_running 1\r\n',
            'STAT version 1.4.14\r\n',
            'END\r\n',
        ])
        result = client.stats()
        tools.assert_equal(client.sock.send_bufs, [
            'stats \r\n'
        ])
        expected = {
            'cmd_get': 2519,
            'cmd_set': 3099,
            'libevent': '2.0.19-stable',
            'hash_is_expanding': False,
            'rusage_user': 0.609165,
            'rusage_system': 0.852791,
            'slab_reassign_running': True,
            'version': '1.4.14',
        }
        tools.assert_equal(result, expected)

    def test_socket_connect(self):
        server = ("example.com", 11211)

        client = Client(server, socket_module=MockSocketModule())
        client._connect()
        tools.assert_equal(client.sock.connections, [server])

        timeout = 2
        connect_timeout = 3
        client = Client(server, connect_timeout=connect_timeout, timeout=timeout,
                        socket_module=MockSocketModule())
        client._connect()
        tools.assert_equal(client.sock.timeouts, [connect_timeout, timeout])

        client = Client(server, socket_module=MockSocketModule())
        client._connect()
        tools.assert_equal(client.sock.socket_options, [])

        client = Client(server, socket_module=MockSocketModule(), no_delay=True)
        client._connect()
        tools.assert_equal(client.sock.socket_options, [(socket.IPPROTO_TCP,
                                                        socket.TCP_NODELAY, 1)])

    def test_python_dict_set_is_supported(self):
        client = self.Client(None)
        client.sock = MockSocket(['STORED\r\n'])
        client['key'] = 'value'

    def test_python_dict_get_is_supported(self):
        client = self.Client(None)
        client.sock = MockSocket(['VALUE key 0 5\r\nvalue\r\nEND\r\n'])
        tools.assert_equal(client['key'], 'value')

    def test_python_dict_get_not_found_is_supported(self):
        client = self.Client(None)
        client.sock = MockSocket(['END\r\n'])

        def _get():
            _ = client['key']

        tools.assert_raises(KeyError, _get)

    def test_python_dict_del_is_supported(self):
        client = self.Client(None)
        client.sock = MockSocket(['DELETED\r\n'])
        del client['key']

class TestMockClient(ClientTestMixin, unittest.TestCase):
    Client = MockMemcacheClient
