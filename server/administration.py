import _thread
import base64
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

        data = client_socket.recv(100000).decode()
        logging.debug(data)
        parts = data.split(':')

        if parts[0] == 'LOGIN':
            username = parts[1]
            one_time_id = parts[2]
            signature = base64.b64decode(parts[3])
            ip = parts[4]
            port = parts[5]
            client_cert = base64.b64decode(parts[6]).decode()

            valid_signature = Cryptography.verify_signature(client_cert, one_time_id, signature)

            if valid_signature and User.login(username, one_time_id):
                client_socket.send('OK'.encode())
            else:
                client_socket.send('NOTOK'.encode())

