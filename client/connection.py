import base64
import logging
import socket
import ssl
from os import getcwd


class Connection:
    """
    Class that abstracts the setup for client connections
    """

    __CA_FILE = '/server.crt'
    __CERT_FILE = '/client.crt'
    __KEY_FILE = '/client.key'

    @staticmethod
    def set_ca_file(file):
        """
        Method to set the CA file

        :param file: File location to be set
        """

        Connection.__CA_FILE = file

    @staticmethod
    def set_cert_file(file):
        """
        Method to set the cert file

        :param file: File location to be set
        """

        Connection.__CERT_FILE = file

    @staticmethod
    def set_key_file(file):
        """
        Method to set the key file

        :param file: File location to be set
        """

        Connection.__KEY_FILE = file

    @staticmethod
    def _initialize_ssl_context():
        """
        Method to initialize the parameters for the SSL connection

        :return: SSL context ready to be used as a wrapper for a socket
        """

        internal_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
                                                      cafile=getcwd() + Connection.__CA_FILE)
        internal_context.load_cert_chain(certfile=getcwd() + Connection.__CERT_FILE,
                                         keyfile=getcwd() + Connection.__KEY_FILE)

        return internal_context

    @staticmethod
    def get_cert():
        """
        Method to return the Client Certificate

        :return: Certificate data encoded in base64
        """

        with open(getcwd() + '/' + Connection.__CERT_FILE, 'rb') as f:
            cert_data = f.read()
            return base64.b64encode(cert_data).decode()

    @staticmethod
    def get_key():
        """
        Method to return the Client Private Key

        :return: Private key
        """

        with open(getcwd() + '/' + Connection.__KEY_FILE, 'r') as f:
            return f.read()

    @staticmethod
    def start_server_connection(server_hostname='127.0.0.1',
                                server_port=8080,
                                server_sni='example.com'):
        """
        Method to start a connection with the server

        :param server_hostname: Server's hostname
        :param server_port: Server's port
        :param server_sni: Server's Name Indication
        :return:
        """

        logging.info('Reaching server on: ' + server_hostname + ':' + str(server_port))
        context = Connection._initialize_ssl_context()
        try:
            internal_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection = context.wrap_socket(internal_socket, server_side=False, server_hostname=server_sni)
            connection.connect((server_hostname, server_port))
            return connection
        except socket.error as exception:
            logging.error(exception)
            print(exception)
            quit(1)

    @staticmethod
    def close(target_socket):
        """
        Method to close a socket

        :param target_socket: Socket to be closed
        """

        target_socket.close()
