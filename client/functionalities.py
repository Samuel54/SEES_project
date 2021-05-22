from connection import Connection


class Functionalities:
    """

    """

    @staticmethod
    def server_functionalities(client, server):
        Functionalities.login(client, server)

    @staticmethod
    def login(client, server):
        username = input('Please insert the username: ')
        one_time_id = input('Please insert the One Time ID: ')
        server.send(f'LOGIN:{username}:{one_time_id}:{client.get_hostname()}'
                    f':{str(client.get_port())}:{Connection.get_cert()}'.encode())
        response = server.recv().decode()
        print(response)
