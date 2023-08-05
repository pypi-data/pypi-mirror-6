import logging
import signal
import sys
import transport

_LOG = logging.getLogger(__name__)


class StdInRelayServer(object):
    """
    StdInRelayServer listens to the STDIN stream and forwards messages over a
    ZeroMQ Push Socket
    """

    def __init__(self, zmq_caster):
        self.zmq_caster = zmq_caster
        self.end_loop = None

    def start(self):
        """
        Start the server's IO loop and bind the ZMQ Caster to the socket
        """
        self.end_loop = False
        self.zmq_caster.bind()

        while not self.end_loop:
            try:
                line = sys.stdin.readline()
                self.zmq_caster.cast(line)
            except Exception as ex:
                _LOG.exception(ex)
                self.end_loop = True

        self.zmq_caster.close()

    def stop(self):
        """
        Stop the server IO loop
        """
        self.end_loop = True


def start_io(bind_ip, bind_port,
             high_water_mark=0, socket_linger=-1):
    """
    Create a new StdInRelayServer, create a signal_handler to stop the
    server when SIGINT is received, and start the server.
    """
    zmq_caster = transport.ZeroMQCaster(
        bind_ip, bind_port, high_water_mark, socket_linger)
    server = StdInRelayServer(zmq_caster)

    def signal_handler(signal, frame):
        server.stop()
        _LOG.info("Hayrack StdInRelayServer stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    _LOG.info("Hayrack StdInRelayServer started!")
    _LOG.info("ZeroMQCaster binding to {0}:{1}".format(bind_ip, bind_port))
    server.start()
