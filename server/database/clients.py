class ClientsStore:
    """
    In memory structure to store the clients that are currently online
    """

    __store = {}

    @staticmethod
    def save_client(username, hostname, port, cert):
        """
        Method to save a new client that is currently online
        :param username: Username of the user that is using the client
        :param hostname: Client's hostname
        :param port: Client's port
        :param cert: Client's certificate
        """

        ClientsStore.__store[username] = {
            'hostname': hostname,
            'port': port,
            'cert': cert
        }

    @staticmethod
    def client_exists(username):
        """
        Method to check if a given user is online (has a registered client online)
        :param username: Username whose connection will be check
        :return: True if the user has a client stored, False if it doesn't
        """

        return username in ClientsStore.__store

    @staticmethod
    def get_client(username):
        """
        Method to fetch a User's Client
        :param username: User whose Client will be fetch
        :return: Client's data
        """
        return ClientsStore.__store[username]
