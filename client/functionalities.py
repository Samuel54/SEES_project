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
            login = Functionalities.login_user(client, server)
        else:
            login = Functionalities.register_client(client, server)

        if login:
            banner = """Select the operation:
  1) List Users
  2) Chat with User
  3) Perform Server Operation
  4) Quit
  > """
            while True:
                option = int(input(banner))
                if option == 1:
                    Functionalities.list_users(client, server)
                elif option == 2:
                    Functionalities.chat_with_user(client, server)
                elif option == 3:
                    Functionalities.server_operations(client, server)
                elif option == 4:
                    Functionalities.shutdown(server)

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
            client.set_username(username)
            print('Login successful and PIN set')
            return True
        else:
            print('Login was not successful, failed on the server')
            return False

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
            return False

        server.send(f'ONLINE:{username}:{client.get_hostname()}:'
                    f'{str(client.get_port())}:{Connection.get_cert()}'.encode())
        response = server.recv(100000).decode()
        if response == 'OK':
            print('Login successful')
            client.set_username(username)
            return True
        else:
            print('Login unsuccessful')
            return False

    @staticmethod
    def list_users(client, server):
        return True

    @staticmethod
    def chat_with_user(client, server):
        return True

    @staticmethod
    def server_operations(client, server):
        """

        """

        operation_options = """Which operation do you want to execute?
    1) Square Root
    2) Cubic Root
    3) N Root
    4) Return
    > """
        option = 0
        while 1 > option or option > 4:
            option = int(input(operation_options))
            if option == 1:
                number = input('Please insert the number on which you want to perform the square root: ')
                result = Functionalities.perform_root(client, server, number, 2)
                if result is not None:
                    print(f'Server calculated: {result} for square root of: {number}.')

            elif option == 2:
                number = input('Please insert the number on which you want to perform the cubic root: ')
                result = Functionalities.perform_root(client, server, number, 3)
                if result is not None:
                    print(f'Server calculated: {result} for square root of: {number}.')

            elif option == 3:
                number = input('Please insert the number on which you want to perform the N root: ')
                n = int(input('Please insert the N you want to perform the root: '))
                result = Functionalities.perform_root(client, server, number, n)
                if result is not None:
                    print(f'Server calculated: {result} for N({n}) root of: {number}.')
            elif option == 4:
                print('Returning...')

    @staticmethod
    def perform_root(client, server, number, n):
        """
        Method to ask the server to calculate a root of a number

        :param client: Client instance, whose properties can be fetched
        :param server: Server connection that will be used to ask for the operation
        :param number: Server number on which the root will be calculated
        :param n: N of the root that needs to be computed
        :return: Result of the number's N root
        """

        signed_username = base64.b64encode(Cryptography.sign(Connection.get_key(), client.get_username())).decode()
        server.send(f'OP:{client.get_username()}:{signed_username}:{n}:{number}'.encode())
        response = server.recv(100000).decode()
        if response == 'UNAUTHORIZED':
            print("You don't have permissions to perform this operation!")
            return None
        if response == 'INVALID':
            print("The values you inserted are not valid!")
            return None
        return float(response)

    @staticmethod
    def shutdown(server):
        """
        Method to shutdown the client app

        :param server: Server socket whose connection will be closed
        """

        Connection.close(server)
        quit(0)
