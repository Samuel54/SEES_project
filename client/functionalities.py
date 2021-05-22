import base64

from connection import Connection
from crypto.helpers import Cryptography


class Functionalities:
    """
        Client set of functionalities
    """

    @staticmethod
    def server_functionalities(client, server):
        """
        Method with all the client's functionalities that can be asked to the server

        :param client: Client instance, whose properties can be fetched
        :param server: Server connection
        """

        if client.pin_exists():
            Functionalities.login_user(client, server)
        else:
            Functionalities.register_client(client, server)

    @staticmethod
    def register_client(client, server):
        """
        Method to login a user in the server

        :param client: Client instance, whose properties can be fetched
        :param server: Server connection
        """

        username = input('Please insert the username:\n> ')
        one_time_id = input('Please insert the One Time ID:\n> ')

        signed_one_time_id = base64.b64encode(Cryptography.sign(Connection.get_key(), one_time_id)).decode()

        server.send(f'LOGIN:{username}:{one_time_id}:{signed_one_time_id}:{client.get_hostname()}'
                    f':{str(client.get_port())}:{Connection.get_cert()}'.encode())
        response = server.recv(100000).decode()
        if response == 'OK':
            pin = input('Please insert your PIN:\n> ')
            client.save_pin(username, pin)
            print('Login successful and PIN set')
        else:
            print('Login was not successful, failed on the server')

    @staticmethod
    def login_user(client, server):
        """
        Method to login a User

        :param client: Client instance, whose properties can be fetched
        :param server: Server connection
        """

        username = input('Please insert the username:\n> ')
        pin = input('Please insert the PIN:\n> ')

        if not client.verify_pin(username, pin):
            print('Username or PIN wrong')
            return

        server.send(f'ONLINE:{username}:{client.get_hostname()}:'
                    f'{str(client.get_port())}:{Connection.get_cert()}'.encode())
        response = server.recv(100000).decode()
        if response == 'OK':
            print('Login successful')
        else:
            print('Login unsuccessful')
