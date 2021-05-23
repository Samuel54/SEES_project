import _thread
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
    RUNNING = True

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
    def _initialize_client_ssl_context():
        """
        Method to initialize the parameters for the SSL connection

        :return: SSL context ready to be used as a wrapper for a socket
        """

        internal_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
                                                      cafile=getcwd() + Connection.__CA_FILE)
        # Hammer here
        internal_context.check_hostname = False
        internal_context.verify_mode = ssl.CERT_NONE

        internal_context.load_cert_chain(certfile=getcwd() + Connection.__CERT_FILE,
                                         keyfile=getcwd() + Connection.__KEY_FILE)

        return internal_context

    @staticmethod
    def _initialize_server_ssl_context():
        """
        Method to initialize the parameters for the SSL connection

        :return: SSL context ready to be used as a wrapper for a socket
        """

        this_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        this_context.verify_mode = ssl.CERT_REQUIRED
        this_context.load_cert_chain(certfile=getcwd() + Connection.__CERT_FILE,
                                     keyfile=getcwd() + Connection.__KEY_FILE)
        this_context.load_verify_locations(cafile=getcwd() + Connection.__CERT_FILE)
        this_context.set_ecdh_curve('prime256v1')

        return this_context

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
        context = Connection._initialize_client_ssl_context()
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
    def start_target_connection(target_hostname,
                                target_port,
                                target_sni='example.com'):
        """
        Method to start a connection with a given client

        :param target_hostname: Target's hostname
        :param target_port: Port's hostname
        :param target_sni: Target's SNI
        """

        logging.info('Reaching client on: ' + target_hostname + ':' + str(target_port))
        context = Connection._initialize_client_ssl_context()
        try:
            internal_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection = context.wrap_socket(internal_socket, server_side=False, server_hostname=target_sni)
            connection.connect((target_hostname, int(target_port)))
            return connection
        except socket.error as exception:
            logging.error(exception)
            print(exception)
            quit(1)

    @staticmethod
    def start_client_connection(hostname,
                                port):
        """

        """

        logging.info('Starting chat with: ' + hostname + ':' + str(port))
        internal_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            internal_socket.bind((hostname, port))
        except socket.error as exception:
            logging.error(exception)
            quit(1)

        logging.info('Socket created and listening...')
        return internal_socket

    @staticmethod
    def accept_connections(listening_socket, client, function_set):
        """
        Method to accept new client connections

        :param listening_socket: Socket that will listen to new connections
        :param client: Client instance to fetch some data
        :param function_set: function with the server's functionalities
        """

        context = Connection._initialize_server_ssl_context()
        listening_socket.listen(5)
        while True:
            if not Connection.RUNNING:
                quit(0)
            try:
                client_socket, client_address = listening_socket.accept()
                logging.info('Accepted connection from:' + client_address[0] + ':' + str(client_address[1]))

                connection = context.wrap_socket(client_socket, server_side=True)
                logging.info('SSL connection established. Peer: {}'.format(connection.getpeercert()))

                _thread.start_new_thread(function_set, (connection, client,))
            except ssl.SSLError as exception:
                logging.error("Failed to accept connection!", exception)

    @staticmethod
    def close(target_socket):
        """
        Method to close a socket

        :param target_socket: Socket to be closed
        """

        target_socket.close()
