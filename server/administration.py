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
    def run_administration(server):
        """
        Method that runs the administration panel

        :param server: Server instance, whose properties can be fetched
        """

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
        print('Welcome to the administration panel!')
        while True:
            option = int(input(banner))
            if option == 1:
                username, one_time_id = User.create()
                print(f'\nUser created with success!\n\tUsername: {username}\n\tOne Time ID: {one_time_id}\n\n')
            elif option == 2:
                print('Quitting server...')
                logging.info('Quitting server...')
                Administration.RUNNING = False
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((server.get_hostname(), server.get_port()))
                _thread.interrupt_main()
                quit(0)
            else:
                print('Option not valid! Try again.')

    @staticmethod
    def server_functionalities(client_socket):
        """
        Method to provide options to the clients

        :param client_socket: Socket where a connection with a client is happening
        """

        if not Administration.RUNNING:
            quit(0)

        data = client_socket.recv().decode()
        logging.debug(data)
        parts = data.split(':')

        if parts[0] == 'LOGIN':
            username = parts[1]
            # TODO: THIS WILL COME CIPHERED, WILL NEED TO DECIPHER
            one_time_id = parts[2]

            ip = parts[3]
            port = parts[4]
            client_cert = parts[5]

            if User.login(username, one_time_id):
                client_socket.send('OK'.encode())
            else:
                client_socket.send('NOTOK'.encode())

