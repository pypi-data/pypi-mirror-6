"""
The transport module defines the classes that serve as the transport layer for
Hayrack when sending messages downstream.  Classes for sending and receiving
are included.
"""

import zmq


class ZeroMQCaster(object):
    """
    ZeroMQCaster allows for messages to be sent downstream by pushing
    messages over a zmq socket to downstream clients.  If multiple clients
    connect to this PUSH socket the messages will be load balanced evenly
    across the clients.
    """

    def __init__(self, bind_host, bind_port,
                 high_water_mark=0, socket_linger=-1):
        """
        Creates an instance of the ZeroMQCaster.  A zmq PUSH socket is
        created and is bound to the specified host:port.

        :param bind_host: ip address to bind to
        :param bind_port: port to bind to
        :param high_water_mark: messages buffered before ZMQ socket.send blocks
        :param socket_linger: time to wait for unsent messages to process on
        socket.close (milliseconds)
        """

        self.socket_type = zmq.PUSH
        self.bind_host = 'tcp://{0}:{1}'.format(bind_host, bind_port)
        self.high_water_mark = int(high_water_mark)
        self.socket_linger = int(socket_linger)
        self.context = None
        self.socket = None
        self.bound = False

    def bind(self):
        """
        Bind the ZeroMQCaster to a host:port to push out messages.
        Create a zmq.Context and a zmq.PUSH socket, and bind the
        socket to the specified host:port
        """
        self.context = zmq.Context()
        self.socket = self.context.socket(self.socket_type)
        #self.socket.set_hwm(self.high_water_mark)
        self.socket.setsockopt(zmq.HWM, self.high_water_mark)
        self.socket.setsockopt(zmq.LINGER, self.socket_linger)
        self.socket.bind(self.bind_host)
        self.bound = True

    def cast(self, msg):
        """
        Sends a message over the zmq PUSH socket
        """
        if not self.bound:
            raise zmq.core.error.ZMQError(
                "ZeroMQCaster is not bound to a socket")
        self.socket.send(msg)

    def close(self):
        """
        Close the zmq socket
        """
        if self.bound:
            self.socket.close()
            self.context.destroy()
            self.socket = None
            self.context = None
            self.bound = False


class ZeroMQReceiver(object):
    """
    ZeroMQReceiver allows for messages to be received by pulling
    messages over a zmq socket from an upstream host.  This client may
    connect to multiple upstream hosts.
    """

    def __init__(self, connect_host_tuples):
        """
        Creates an instance of the ZeroMQReceiver.

        :param connect_host_tuples: [(host, port), (host, port)],
        for example [('127.0.0.1', '5000'), ('127.0.0.1', '5001')]
        """
        self.upstream_hosts = [
            "tcp://{}:{}".format(*host_tuple)
            for host_tuple in connect_host_tuples]
        self.socket_type = zmq.PULL
        self.context = None
        self.socket = None
        self.connected = False

    def connect(self):
        """
        Connect the receiver to upstream hosts.  Create a zmq.Context
        and a zmq.PULL socket, and is connect the socket to all
        specified host:port tuples.
        """
        self.context = zmq.Context()
        self.socket = self.context.socket(self.socket_type)

        for host in self.upstream_hosts:
            self.socket.connect(host)

        self.connected = True

    def get(self):
        """
        Read a message form the zmq socket and return
        """
        if not self.connected:
            raise zmq.core.error.ZMQError(
                "ZeroMQReceiver is not connected to a socket")
        return self.socket.recv()

    def close(self):
        """
        Close the zmq socket
        """
        if self.connected:
            self.socket.close()
            self.context.destroy()
            self.socket = None
            self.context = None
            self.connected = False
