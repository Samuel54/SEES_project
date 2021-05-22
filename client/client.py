import logging
import os
import sys

from functionalities import Functionalities
from connection import Connection


class Client:
    _hostname = '127.0.0.1'
    _port = 8081

    @staticmethod
    def get_hostname():
        """
        Method to get the server's hostname

        :return: Server's hostname
        """

        return Client._hostname

    @staticmethod
    def set_hostname(hostname):
        """
        Method to set the server's hostname

        :param hostname: Hostname to be set
        """

        Client._hostname = hostname

    @staticmethod
    def get_port():
        """
        Method to get the port where the server is listening

        :return: Port used
        """

        return Client._port

    @staticmethod
    def set_port(port):
        """
        Method to set the port where connections will be listened

        :param port: Port to be set
        """

        Client._port = port

    @staticmethod
    def start_client():
        """
        Function responsible for running the connections and client bootstrap
        """

        # Creates a connection with the server
        server_connection = Connection.start_server_connection()
        # Listens to the port waiting for clients, for each client, setups a new thread for interaction
        Functionalities.server_functionalities(Client, server_connection)
        # Closes the socket when ending everything
        Connection.close(server_connection)


def main():
    """
    Main thread
    """

    logging.basicConfig(filename='logs.log', level=logging.INFO, filemode='a')
    Client.start_client()


if __name__ == '__main__':
    """
    Method to handle the program closing 
    """

    try:
        main()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
