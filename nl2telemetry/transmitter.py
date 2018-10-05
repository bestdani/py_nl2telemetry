import socket
import binascii


class TcpTransmitter:
    """
    A simple wrapper around a socket for connecting with the telemetry server
    of NL2.
    """

    def __init__(self, tcp_ip='127.0.0.1', tcp_port=15151):
        self.tcp_ip = tcp_ip
        self.tcp_port = tcp_port

    def connect(self):
        ip_port_msg = "{}:{}".format(self.tcp_ip, self.tcp_port)
        print("NL2 transmitter connecting to", ip_port_msg)

        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sck.settimeout(3)
        try:
            self.sck.connect((self.tcp_ip, self.tcp_port))
        except Exception as e:
            raise e

    def send(self, msg):
        self.sck.send(msg.buffer)

    def receive(self, buffer_size=100):
        return self.sck.recv(buffer_size)

    def close(self):
        self.sck.close()
        print("connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
