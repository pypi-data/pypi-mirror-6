from gevent.socket import socket
from gevent.queue import Queue

from rexpro.exceptions import RexProConnectionException
from rexpro.messages import ErrorResponse

from contextlib import contextmanager
import struct

from rexpro import exceptions
from rexpro import messages


class RexProSocket(socket):
    """ Subclass of python's socket that sends and received rexpro messages """

    def send_message(self, msg):
        """
        Serializes the given message and sends it to rexster

        :param msg: the message instance to send to rexster
        :type msg: RexProMessage
        """
        self.send(msg.serialize())

    def get_response(self):
        """
        gets the message type and message from rexster


        Basic Message Structure:  reference: https://github.com/tinkerpop/rexster/wiki/RexPro-Messages
            segment             | type (bytes)  | description
            protocol version    | byte (1)      | Version of RexPro, should be 1
            serializer type     | byte (1)      | Type of Serializer: msgpack==0, json==1
            reserved for future | byte (4)      | Reserved for future use.
            message type        | byte (1)      | Tye type of message as described in the value columns.
            message size        | int (4)       | The length of the message body
            message body        | byte (n)      | The body of the message itself. The Good, Bad and Ugly.


        Message Types
            message type  | type     | value | description
            session       | request  | 1     | A request to open or close the session with the RexPro Server
            session       | response | 2     | RexPro server response to session request
            script        | request  | 3     | A request to process a gremlin script
            script        | response | 5     | A response to a script request
            error         | response | 0     | A RexPro server error response

        :returns: RexProMessage
        """
        msg_version = self.recv(1)
        if not msg_version:  # pragma: no cover
            # Can only be tested against a known broken version - none known yet.
            raise exceptions.RexProConnectionException('socket connection has been closed')
        if bytearray([msg_version])[0] != 1:  # pragma: no cover
            # Can only be tested against a known broken version - none known yet.
            raise exceptions.RexProConnectionException('unsupported protocol version: {}'.format(msg_version))

        serializer_type = self.recv(1)
        if bytearray(serializer_type)[0] != 0:  # pragma: no cover
            # Can only be tested against a known broken version - none known yet.
            raise exceptions.RexProConnectionException('unsupported serializer version: {}'.format(serializer_type))

        # get padding
        self.recv(4)

        msg_type = self.recv(1)
        msg_type = bytearray(msg_type)[0]

        msg_len = struct.unpack('!I', self.recv(4))[0]

        if msg_len == 0:  # pragma: no cover
            # This shouldn't happen unless there is a server-side problem
            raise exceptions.RexProScriptException("Insufficient data received")

        response = ''
        while len(response) < msg_len:
            response += self.recv(msg_len)

        MessageTypes = messages.MessageTypes

        type_map = {
            MessageTypes.ERROR: messages.ErrorResponse,
            MessageTypes.SESSION_RESPONSE: messages.SessionResponse,
            MessageTypes.SCRIPT_RESPONSE: messages.MsgPackScriptResponse
        }

        if msg_type not in type_map:  # pragma: no cover
            # this shouldn't happen unless there is an unknown rexpro version change
            raise exceptions.RexProConnectionException("can't deserialize message type {}".format(msg_type))
        return type_map[msg_type].deserialize(response)


class RexProConnectionPool(object):

    def __init__(self, host, port, graph_name, graph_obj_name='g', username='', password='', timeout=None,
                 pool_size=10):
        """
        Connection constructor

        :param host: the server to connect to
        :type host: str (ip address)
        :param port: the server port to connect to
        :type port: int
        :param graph_name: the graph to connect to
        :type graph_name: str
        :param graph_obj_name: The graph object to use
        :type graph_obj_name: str
        :param username: the username to use for authentication (optional)
        :type username: str
        :param password: the password to use for authentication (optional)
        :type password: str
        :param pool_size: the initial connection pool size
        :type pool_size: int
        """

        self.host = host
        self.port = port
        self.graph_name = graph_name
        self.graph_obj_name = graph_obj_name
        self.username = username
        self.password = password
        self.timeout = timeout

        self.pool_size = pool_size
        self.pool = Queue()
        self.size = 0

    def get(self, *args, **kwargs):
        """ Retrieve a rexpro connection from the pool

        :param host: the rexpro server to connect to
        :type host: str (ip address)
        :param port: the rexpro server port to connect to
        :type port: int
        :param graph_name: the graph to connect to
        :type graph_name: str
        :param graph_obj_name: The graph object to use
        :type graph_obj_name: str
        :param username: the username to use for authentication (optional)
        :type username: str
        :param password: the password to use for authentication (optional)
        :type password: str
        :rtype: RexProConnection
        """
        pool = self.pool
        if self.size >= self.pool_size or pool.qsize():
            return pool.get()
        else:
            self.size += 1
            try:
                new_item = self._create_connection(*args, **kwargs)
            except:
                self.size -= 1
                raise
            return new_item

    def put(self, conn):
        """ Restore a connection to the pool

        :param conn: A rexpro connection to restore to the pool
        :type conn: RexProConnection
        """
        self.pool.put(conn)

    def close_all(self):
        """ Close all pool connections for a clean shutdown """
        while not self.pool.empty():
            conn = self.pool.get_nowait()
            try:
                conn.close()
            except Exception:
                pass

    @contextmanager
    def connection(self, *args, **kwargs):
        """ Context manager that conveniently grabs a connection from the pool and provides it with the context
        cleanly closes up the connection and restores it to the pool afterwards

        :param host: the rexpro server to connect to
        :type host: str (ip address)
        :param port: the rexpro server port to connect to
        :type port: int
        :param graph_name: the graph to connect to
        :type graph_name: str
        :param graph_obj_name: The graph object to use
        :type graph_obj_name: str
        :param username: the username to use for authentication (optional)
        :type username: str
        :param password: the password to use for authentication (optional)
        :type password: str
        """
        conn = self.create_connection(*args, **kwargs)
        if not conn:
            raise RexProConnectionException("Cannot commit because connection was closed: %r" % (conn, ))
        with conn.transaction:
            yield
        if conn is not None:
            self.close_connection(conn)

    def _create_connection(self, host=None, port=None, graph_name=None, graph_obj_name=None, username=None,
                           password=None, timeout=None):
        """ Create a RexProConnection using the provided parameters, defaults to Pool defaults

        :param host: the rexpro server to connect to
        :type host: str (ip address)
        :param port: the rexpro server port to connect to
        :type port: int
        :param graph_name: the graph to connect to
        :type graph_name: str
        :param graph_obj_name: The graph object to use
        :type graph_obj_name: str
        :param username: the username to use for authentication (optional)
        :type username: str
        :param password: the password to use for authentication (optional)
        :type password: str
        :rtype: RexProConnection
        """
        return RexProConnection(host=host or self.host,
                                port=port or self.port,
                                graph_name=graph_name or self.graph_name,
                                graph_obj_name=graph_obj_name or self.graph_obj_name,
                                username=username or self.username,
                                password=password or self.password,
                                timeout=timeout or self.timeout)

    def create_connection(self, *args, **kwargs):
        """ Get a connection from the pool if available, otherwise return a new connection if the pool isn't full

        :param host: the rexpro server to connect to
        :type host: str (ip address)
        :param port: the rexpro server port to connect to
        :type port: int
        :param graph_name: the graph to connect to
        :type graph_name: str
        :param graph_obj_name: The graph object to use
        :type graph_obj_name: str
        :param username: the username to use for authentication (optional)
        :type username: str
        :param password: the password to use for authentication (optional)
        :type password: str
        :rtype: RexProConnection
        """
        return self.get(*args, **kwargs)

    def close_connection(self, conn):
        """ Close a connection and restore it to the pool

        :param conn: a rexpro connection that was pull from the Pool
        :type conn: RexProConnection
        """
        conn.close()
        self.put(conn)


class RexProConnection(object):

    def __init__(self, host, port, graph_name, graph_obj_name='g', username='', password='', timeout=None):
        """
        Connection constructor

        :param host: the rexpro server to connect to
        :type host: str (ip address)
        :param port: the rexpro server port to connect to
        :type port: int
        :param graph_name: the graph to connect to
        :type graph_name: str
        :param graph_obj_name: The graph object to use
        :type graph_obj_name: str
        :param username: the username to use for authentication (optional)
        :type username: str
        :param password: the password to use for authentication (optional)
        :type password: str
        """
        self.host = host
        self.port = port
        self.graph_name = graph_name
        self.graph_obj_name = graph_obj_name
        self.username = username
        self.password = password
        self.timeout = timeout

        self.graph_features = None

        # connect to server
        self._conn = RexProSocket()
        self._conn.settimeout(self.timeout)
        try:
            self._conn.connect((self.host, self.port))
        except Exception as e:
            raise RexProConnectionException("Could not connect to database: %s" % e)

        # indicates that we're in a transaction
        self._in_transaction = False

        # stores the session key
        self._session_key = None
        self._open_session()

    def _open_session(self):
        """ Creates a session with rexster and creates the graph object """
        self._conn.send_message(
            messages.SessionRequest(
                username=self.username,
                password=self.password,
                graph_name=self.graph_name
            )
        )
        response = self._conn.get_response()
        if isinstance(response, ErrorResponse):
            raise RexProConnectionException(response.message)
        self._session_key = response.session_key

        self.graph_features = self.execute('g.getFeatures().toMap()')

    def open_transaction(self):
        """ opens a transaction """
        if self._in_transaction:
            raise exceptions.RexProScriptException("transaction is already open")
        self.execute(
            script='g.stopTransaction(FAILURE)',
            isolate=False
        )
        self._in_transaction = True

    def close_transaction(self, success=True):
        """
        closes an open transaction

        :param success: indicates which status to close the transaction with, True will commit the changes, False will roll them back
        :type success: bool
        """
        if not self._in_transaction:
            raise exceptions.RexProScriptException("transaction is not open")
        self.execute(
            script='g.stopTransaction({})'.format('SUCCESS' if success else 'FAILURE'),
            isolate=False
        )
        self._in_transaction = False

    def close(self):
        """ Close a connection """
        self._conn.send_message(
            messages.SessionRequest(
                session_key=self._session_key,
                graph_name=self.graph_name,
                kill_session=True
            )
        )
        response = self._conn.get_response()
        if isinstance(response, ErrorResponse):
            raise RexProConnectionException(response.message)

    @contextmanager
    def transaction(self):
        """
        Context manager that opens a transaction and closes it at
        the end of it's code block, use with the 'with' statement
        """
        self.open_transaction()
        yield
        self.close_transaction()

    def execute(self, script, params={}, isolate=True, transaction=True, pretty=False):
        """
        executes the given gremlin script with the provided parameters

        :param script: the gremlin script to isolate
        :type script: str
        :param params: the parameters to execute the script with
        :type params: dictionary
        :param isolate: wraps the script in a closure so any variables set aren't persisted for the next execute call
        :type isolate: bool
        :param transaction: query will be wrapped in a transaction if set to True (default)
        :type transaction: bool
        :param pretty: will dedent the script if set to True
        :type pretty: bool

        :rtype: list
        """
        self._conn.send_message(
            messages.ScriptRequest(
                script=script,
                params=params,
                session_key=self._session_key,
                isolate=isolate,
                in_transaction=transaction
            )
        )
        response = self._conn.get_response()

        if isinstance(response, messages.ErrorResponse):
            raise exceptions.RexProScriptException(response.message)

        return response.results
