import _thread
import logging
import socket
import ssl

from administration import Administration


class Connection:
    """
    Class that abstracts all the setup of new connections
    """

    @staticmethod
    def start_socket(hostname='localhost', port=8080):
        """
        Method to start the server socket

        :param hostname: Hostname on which the server will reply
        :param port: Port from which the server will listen to
        :return: Initialized socket ready to listen for new connections
        """

        logging.info('Starting server on: ' + hostname + ':' + str(port))
        internal_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            internal_socket.bind((hostname, port))
        except socket.error as exception:
            logging.error(exception)
            quit(1)

        logging.info('Socket created and listening...')
        return internal_socket

    @staticmethod
    def _initialize_ssl_context():
        """
        Method to initialize the parameters for the SSL connection

        :return: SSL context ready to be used as a wrapper for a socket
        """

        internal_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        internal_context.verify_mode = ssl.CERT_REQUIRED
        internal_context.load_cert_chain(certfile='server.crt', keyfile='server.key')
        internal_context.load_verify_locations(cafile='client.crt')
        internal_context.set_ecdh_curve('prime256v1')

        return internal_context

    @staticmethod
    def accept_connections(listening_socket, function_set):
        """
        Method to accept new client connections

        :param function_set: function with the server's functionalities
        :param listening_socket: Socket that will listen to new connections
        """

        context = Connection._initialize_ssl_context()
        listening_socket.listen(5)
        while True:
            if not Administration.RUNNING:
                quit(0)
            try:
                client_socket, client_address = listening_socket.accept()
                logging.info('Accepted connection from:' + client_address[0] + ':' + str(client_address[1]))

                connection = context.wrap_socket(client_socket, server_side=True)
                logging.info('SSL connection established. Peer: {}'.format(connection.getpeercert()))

                _thread.start_new_thread(function_set, (connection,))
            except ssl.SSLError as exception:
                logging.error("Failed to accept connection!", exception)

    @staticmethod
    def close(server_socket):
        """
        Method to close a socket

        :param server_socket: Socket to be closed
        """

        server_socket.close()
