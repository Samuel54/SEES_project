import _thread
import base64
import logging
import socket

from crypto.helpers import Cryptography
from database.clients import ClientsStore
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
        try:
            data = client_socket.recv(100000).decode()
            logging.debug(data)
            parts = data.split(':')

            if parts[0] == 'LOGIN':
                Administration.register_user(client_socket, parts)
            elif parts[0] == 'ONLINE':
                Administration.set_user_online(client_socket, parts)
        except ConnectionResetError:
            host, port = client_socket.getpeername()
            username = ClientsStore.reverse_lookup(host, port)
            if username is not None:
                ClientsStore.set_offline(username)

    @staticmethod
    def register_user(client_socket, parts):
        """
        Method to register users and their clients

        :param client_socket: Socket where a connection with a client is happening
        :param parts: Parts of the message that was sent by the client
        """

        username = parts[1]
        one_time_id = parts[2]
        signature = base64.b64decode(parts[3])
        hostname = parts[4]
        port = parts[5]
        client_cert = parts[6]

        valid_signature = Cryptography.verify_signature(base64.b64decode(client_cert).decode(),
                                                        one_time_id,
                                                        signature)

        if valid_signature and User.login(username, one_time_id):
            ClientsStore.save_client(username, hostname, port, client_cert)
            ClientsStore.set_online(username, hostname, port)
            client_socket.send('OK'.encode())
        else:
            client_socket.send('NOTOK'.encode())

    @staticmethod
    def set_user_online(client_socket, parts):
        """
        Method to register users and their clients

        :param client_socket: Socket where a connection with a client is happening
        :param parts: Parts of the message that was sent by the client
        """

        username = parts[1]
        hostname = parts[2]
        port = parts[3]
        client_cert = parts[4]

        if ClientsStore.client_exists(username):
            client = ClientsStore.get_client(username)
            if client_cert != client['cert']:
                client_socket.send('NOTOK'.encode())
            else:
                ClientsStore.update_client(username, hostname, port, client_cert)
                ClientsStore.set_online(username, hostname, port)
                client_socket.send('OK'.encode())
        else:
            client_socket.send('NOTOK'.encode())
