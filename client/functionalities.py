from connection import Connection


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

        Functionalities.login(client, server)

    @staticmethod
    def login(client, server):
        """
        Method to login a user in the server

        :param client: Client instance, whose properties can be fetched
        :param server: Server connection
        """

        username = input('Please insert the username: ')
        one_time_id = input('Please insert the One Time ID: ')
        server.send(f'LOGIN:{username}:{one_time_id}:{client.get_hostname()}'
                    f':{str(client.get_port())}:{Connection.get_cert()}'.encode())
        response = server.recv().decode()
        print(response)
