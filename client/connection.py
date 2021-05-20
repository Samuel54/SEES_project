import _thread
import logging
import socket
import ssl


class Connection:
    """
    Class that abstracts the setup for client connections
    """

    @staticmethod
    def _initialize_ssl_context():
        """
        Method to initialize the parameters for the SSL connection
        :return: SSL context ready to be used as a wrapper for a socket
        """

        internal_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile='server.crt')
        internal_context.load_cert_chain(certfile='client.crt', keyfile='client.key')

        return internal_context

    @staticmethod
    def start_server_connection(server_hostname='127.0.0.1',
                                server_port=8080,
                                server_sni='example.com'):
        """

        :param server_hostname:
        :param server_port:
        :param server_sni:
        :return:
        """

        logging.info('Reaching server on: ' + server_hostname + ':' + str(server_port))
        context = Connection._initialize_ssl_context()
        try:
            internal_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection = context.wrap_socket(internal_socket, server_side=False, server_hostname=server_sni)
            connection.connect((server_hostname, server_port))
        except socket.error as exception:
            logging.error(exception)
            print(exception)
            quit(1)

        result = connection.recv(1024)
        print(result.decode())
        connection.close()
