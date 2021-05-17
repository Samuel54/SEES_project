import _thread
import logging
import socket

from crypto.helpers import Cryptography
from user import User


class Administration:
    """
    Class that has all the control over all the server's functionalities
    """

    RUNNING = True

    @staticmethod
    def run_administration(Server):
        if Cryptography.get_passphrase() == "":
            while len(Cryptography.get_passphrase()) != 32:
                passphrase = input("Please insert the server's passphrase (32 characters): ")
                Cryptography.set_passphrase(passphrase)

        """
        Method to start the menu used by the administrator
        """

        banner = """What do you want to do?
    1 - Create user
    2 - Quit
    > """
        print("Welcome to the administration panel!")
        while True:
            option = int(input(banner))
            if option == 1:
                User.create()
            elif option == 2:
                print("Quitting server...")
                logging.info("Quitting server...")
                Administration.RUNNING = False
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((Server.get_hostname(), Server.get_port()))
                _thread.interrupt_main()
                quit(0)
            else:
                print("Option not valid! Try again.")

    @staticmethod
    def server_functionalities(client_socket):
        """
        Method to provide options to the clients
        :param client_socket: Socket where a connection with a client is happening
        """

        if not Administration.RUNNING:
            quit(0)
