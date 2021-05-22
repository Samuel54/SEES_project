import _thread
import logging
import os
import sys

from connection import Connection
from administration import Administration


class Server:
    """
    Main server implementation. This is the class that will be run on main.
    """

    _hostname = '127.0.0.1'
    _port = 8080

    @staticmethod
    def get_hostname():
        """
        Method to get the server's hostname

        :return: Server's hostname
        """

        return Server._hostname

    @staticmethod
    def set_hostname(hostname):
        """
        Method to set the server's hostname

        :param hostname: Hostname to be set
        """

        Server._hostname = hostname

    @staticmethod
    def get_port():
        """
        Method to get the port where the server is listening

        :return: Port used
        """

        return Server._port

    @staticmethod
    def set_port(port):
        """
        Method to set the port where connections will be listened

        :param port: Port to be set
        """

        Server._port = port

    @staticmethod
    def start_server():
        """
        Function responsible for running the connections and server bootstrap
        """

        # Binds a socket to a specific port
        server_socket = Connection.start_socket(hostname=Server.get_hostname(), port=Server.get_port())
        # Listens to the port waiting for clients, for each client, setups a new thread for interaction
        Connection.accept_connections(server_socket, Administration.server_functionalities)
        # Closes the socket when ending everything
        server_socket.close()


def main():
    """
    Main thread
    """

    logging.basicConfig(filename='logs.log', level=logging.DEBUG, filemode='a')
    _thread.start_new_thread(Administration.run_administration, (Server,))
    Server.start_server()


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
