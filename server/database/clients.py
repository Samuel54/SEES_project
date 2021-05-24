import base64
from os import getcwd, path, remove, rename

from crypto.helpers import Cryptography
from user import User


class ClientsStore:
    """
    In memory structure to store the clients that are currently online
    """

    __DB_FILENAME = "/client_registry"
    __online = {}

    @staticmethod
    def save_client(username, hostname, port, cert):
        """
        Method to save a new client that is currently online

        :param username: Username of the user that is using the client
        :param hostname: Client's hostname
        :param port: Client's port
        :param cert: Client's certificate
        """

        data = f'{hostname}:{port}:{cert}'
        hashed_username = base64.b64encode(Cryptography.hash(username).digest()).decode()
        file = open(getcwd() + ClientsStore.__DB_FILENAME, 'a')
        iv, ciphered_data = Cryptography.cipher(Cryptography.get_passphrase(), data)
        file.write(hashed_username + ':' + ciphered_data.hex() + '.' + iv.hex() + '\n')
        file.flush()
        file.close()

    @staticmethod
    def client_exists(username):
        """
        Method to check if a given user is online (has a registered client online)

        :param username: Username whose connection will be check
        :return: True if the user has a client stored, False if it doesn't
        """

        hashed_username = base64.b64encode(Cryptography.hash(username).digest()).decode()

        if path.exists(getcwd() + ClientsStore.__DB_FILENAME):
            with open(getcwd() + ClientsStore.__DB_FILENAME, 'r') as f:
                for entry in f:
                    parts = entry.split(':')
                    if parts[0] == hashed_username:
                        return True
                return False
        else:
            return False

    @staticmethod
    def get_client(username):
        """
        Method to fetch a User's Client

        :param username: User whose Client will be fetch
        :return: Client's data
        """

        data = None
        hashed_username = base64.b64encode(Cryptography.hash(username).digest()).decode()
        with open(getcwd() + ClientsStore.__DB_FILENAME, 'r') as f:
            for entry in f:
                parts = entry.split(':')
                if parts[0] == hashed_username:
                    material = parts[1].split('.')
                    ciphertext = bytearray.fromhex(material[0])
                    iv = bytearray.fromhex(material[1])
                    data = Cryptography.decipher(Cryptography.get_passphrase(), ciphertext, iv).decode()
        client_info = data.split(':')

        return {
            'hostname': client_info[0],
            'port': client_info[1],
            'cert': client_info[2]
        }

    @staticmethod
    def list_users(username, clearance_level):
        """
        Method to list the User's that are online and which clearance level is compatible with the asking user

        :param username: Username of the user that is asking for the list
        :param clearance_level: Clearance level of the user that is asking for the list
        :return: List of online users that the user can see
        """

        user_list = []
        for user in ClientsStore.__online:
            if user != username:
                if ClientsStore.is_online(username):
                    saved_user = User.load_user(user)
                    if saved_user.get_clearance_level() <= clearance_level:
                        user_entry = ClientsStore.get_client(user)
                        user_entry['username'] = user
                        user_list.append(user_entry)
        return user_list

    @staticmethod
    def update_client(username, hostname, port, cert):
        """
        Method to update a client from the database

        :param username: Username that targets the client to be updated
        :param hostname: Hostname to be updated
        :param port: Port to be updated
        :param cert: Certificate to be updated
        """

        hashed_username = base64.b64encode(Cryptography.hash(username).digest()).decode()
        data = f'{hostname}:{port}:{cert}'
        with open(getcwd() + ClientsStore.__DB_FILENAME) as file_input, \
                open(getcwd() + ClientsStore.__DB_FILENAME + '.temp', 'w') as file_output:
            for entry in file_input:
                new_entry = entry
                if entry.split(':')[0] == hashed_username:
                    iv, ciphered_data = Cryptography.cipher(Cryptography.get_passphrase(), data)
                    new_entry = hashed_username + ':' + ciphered_data.hex() + '.' + iv.hex() + '\n'
                file_output.write(new_entry)
            if path.exists(getcwd() + ClientsStore.__DB_FILENAME):
                remove(getcwd() + ClientsStore.__DB_FILENAME)
                rename(getcwd() + ClientsStore.__DB_FILENAME + '.temp', getcwd() + ClientsStore.__DB_FILENAME)

    @staticmethod
    def set_online(username, hostname, port):
        """
        Method to set a User online

        :param username: Username of the user to save on the online list
        :param hostname: User's Client hostname
        :param port: User's Client port
        """

        ClientsStore.__online[username] = {
            'online': True,
            'hostname': hostname,
            'port': port
        }

    @staticmethod
    def set_offline(username):
        """
        Method to set a User offline

        :param username: Username of the user to set offline
        """

        if username in ClientsStore.__online:
            ClientsStore.__online[username]['online'] = False

    @staticmethod
    def is_online(username):
        """
        Method to check if a User is online

        :return: True if it is, false otherwise
        """

        return ClientsStore.__online[username]

    @staticmethod
    def reverse_lookup(hostname, port):
        """
        Method to check whose User belongs a given client

        :param hostname: Client's hostname
        :param port: Client's port
        :return: True if it is known, false otherwise
        """

        for client in ClientsStore.__online:
            if ClientsStore.__online[client]['hostname'] == hostname \
                    and ClientsStore.__online[client]['port'] == port:
                return client['username']
        return None
