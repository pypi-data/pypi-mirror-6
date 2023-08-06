from .connection import Connection
from .exceptions import NoAvailableConnectionsInPoolError
from .protocol import MongoProtocol
import asyncio


__all__ = ('Pool', )


class Pool:
    """
    Pool of connections. Each
    Takes care of setting up the connection and connection pooling.

    When pool_size > 1 and some connections are in use because of transactions
    or blocking requests, the other are preferred.

    ::

        pool = yield from Pool.create(host='localhost', port=6379, pool_size=10)
        result = yield from connection.set('key', 'value')
    """

    protocol = MongoProtocol
    """
    The :class:`MongoProtocol` class to be used for each connection in this pool.
    """

    @classmethod
    def get_connection_class(cls):
        """
        Return the :class:`Connection` class to be used for every connection in
        this pool. Normally this is just a ``Connection`` using the defined ``protocol``.
        """
        class ConnectionClass(Connection):
            protocol = cls.protocol
        return ConnectionClass

    @classmethod
    @asyncio.coroutine
    def create(cls, host='localhost', port=6379, loop=None, password=None, db=0, pool_size=1, auto_reconnect=True):
        """
        Create a new connection instance.
        """
        self = cls()
        self._host = host
        self._port = port
        self._pool_size = pool_size

        # Create connections
        self._connections = []

        for i in range(pool_size):
            connection_class = cls.get_connection_class()
            connection = yield from connection_class.create(host=host, port=port, loop=loop,
                            password=password, db=db, auto_reconnect=auto_reconnect)
            self._connections.append(connection)

        return self

    def __repr__(self):
        return 'Pool(host=%r, port=%r, pool_size=%r)' % (self._host, self._port, self._poolsize)

    @property
    def pool_size(self):
        """ Number of parallel connections in the pool."""
        return self._poolsize

    @property
    def connections_in_use(self):
        """
        Return how many protocols are in use.
        """
        return sum([ 1 for c in self._connections if c.protocol.in_use ])

    @property
    def connections_connected(self):
        """
        The amount of open TCP connections.
        """
        return sum([ 1 for c in self._connections if c.protocol.is_connected ])

    def close(self):
        for conn in self._connections:
            conn.disconnect()

    def _get_free_connection(self):
        """
        Return the next protocol instance that's not in use.
        (A protocol in pubsub mode or doing a blocking request is considered busy,
        and can't be used for anything else.)
        """
        self._shuffle_connections()

        for c in self._connections:
            if c.protocol.is_connected and not c.protocol.in_use:
                return c

    def _shuffle_connections(self):
        """
        'shuffle' protocols. Make sure that we divide the load equally among the protocols.
        """
        self._connections = self._connections[1:] + self._connections[:1]

    def __getattr__(self, name):
        """
        Proxy to a protocol. (This will choose a protocol instance that's not
        busy in a blocking request or transaction.)
        """

        if 'close' == name:
            return self.close

        connection = self._get_free_connection()

        if connection:
            return getattr(connection, name)
        else:
            raise NoAvailableConnectionsInPoolError('No available connections in the pool: size=%s, in_use=%s, connected=%s' % (
                                self.pool_size, self.connections_in_use, self.connections_connected))
