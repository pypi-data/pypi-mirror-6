import os

from eventlet.greenthread import sleep
from eventlet.queue import LightQueue
from eventlet.queue import Empty

from redis import Redis, ConnectionPool
from redis.exceptions import ConnectionError
from redis.connection import UnixDomainSocketConnection, Connection
from redis_cache.client.default import DefaultClient

from django.conf import settings

_connection_pools = {}

class EventletConnectionPool(ConnectionPool):
    def __init__(self, connection_class=Connection, max_connections=None,
                 **connection_kwargs):
        self.pid = os.getpid()
        self.connection_class = connection_class
        self.connection_kwargs = connection_kwargs
        self.max_connections = max_connections or 2 ** 31
        self._created_connections = 0
        self._available_connections = LightQueue()
        self._in_use_connections = set()
    def get_connection(self, command_name, *keys, **options):
        "Get a connection from the pool"
        try:
            connection = self._available_connections.get_nowait()
        except Empty:
            if self._created_connections < self.max_connections:
                connection = self.make_connection()
            else:
                try:
                    connection = self._available_connections.get()
                except Empty:
                    raise ConnectionError("Couldn't find a free connection")
        self._in_use_connections.add(connection)
        return connection
    def release(self, connection):
        "Releases the connection back to the pool"
        self._checkpid()
        if connection.pid == self.pid:
            self._in_use_connections.remove(connection)
            self._available_connections.put_nowait(connection)
    def disconnect(self):
        "Disconnects all connections in the pool"
        while True:
            try:
                self._available_connections.get_nowait().disconnect()
            except Empty:
                break
        for connection in self._in_use_connections:
            connection.disconnect()

def get_or_create_connection_pool(**params):
    global _connection_pools

    key = str(params)
    if key not in _connection_pools:
        _connection_pools[key] = EventletConnectionPool(**params)
    return _connection_pools[key]


class EventletConnectionClient(DefaultClient):
    def _connect(self, host, port, db):
        """
Creates a redis connection with connection pool.
"""

        kwargs = {
            "db": db,
            "parser_class": self.parser_class,
            "password": self._options.get('PASSWORD', None),
            "max_connections": settings.REDIS_POOL_SIZE,
        }

        if host == "unix":
            kwargs.update({'path': port, 'connection_class': UnixDomainSocketConnection})
        else:
            kwargs.update({'host': host, 'port': port, 'connection_class': Connection})

        connection_pool = get_or_create_connection_pool(**kwargs)
        connection = Redis(connection_pool=connection_pool)
        return connection