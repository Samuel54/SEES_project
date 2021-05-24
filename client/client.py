import _thread
import logging
import os
import sys

from connection import Connection
from crypto.helpers import Cryptography
from functionalities import Functionalities


class Client:
    _hostname = '127.0.0.1'
    _port = 8081
    _pin = ''
    _LOCAL_DATA_FILE = '/data'
    _username = ''
    _users_store = {}

    @staticmethod
    def set_local_file(filename):
        """
        Method to set the file where the data will be stored

        :param filename: File to be set
        """

        Client._LOCAL_DATA_FILE = filename

    @staticmethod
    def add_user(username, hostname, port, cert):
        """
        Method to add a online user to a in-memory structure

        :param username: Username to be saved
        :param hostname: Hostname to be saved
        :param port: Port to be saved
        :param cert: Cert to be saved
        """

        Client._users_store[username] = {
            'hostname': hostname,
            'port': port,
            'certificate': cert
        }

    @staticmethod
    def get_user(username):
        """
        Method to get a online user from the in-memory structure

        :param username: Username to be fetched
        :return: Where can that user be contacted
        """

        return Client._users_store[username]

    @staticmethod
    def list_users():
        return list(Client._users_store)

    @staticmethod
    def remove_user(username):
        """
        Method to remove a online user from the in-memory structure

        :param username: Username to be removed
        """

        Client._users_store.pop(username, None)

    @staticmethod
    def get_hostname():
        """
        Method to get the server's hostname

        :return: Server's hostname
        """

        return Client._hostname

    @staticmethod
    def set_hostname(hostname):
        """
        Method to set the server's hostname

        :param hostname: Hostname to be set
        """

        Client._hostname = hostname

    @staticmethod
    def get_username():
        """
        Method to get the user's username

        :return: User's username
        """

        return Client._username

    @staticmethod
    def set_username(username):
        """
        Method to set the user's username

        :param username: Username to be set
        """

        Client._username = username

    @staticmethod
    def set_pin(pin):
        """
        Method to save the user's PIN in memory

        :param pin: PIN to be set
        """

        Client._pin = pin

    @staticmethod
    def save_pin(username, pin):
        """
        Method to persist the user's PIN

        :param username: Username to be saved into the filesystem
        :param pin: PIN to be saved into the filesystem
        """

        hashed_pin = Cryptography.hash_data(f'{username}:{pin}')
        with open(os.getcwd() + Client._LOCAL_DATA_FILE, 'w') as f:
            f.write(hashed_pin.hex()+'\n')
        f.close()
        Client.set_pin(pin)

    @staticmethod
    def pin_exists():
        """
        Method to verify if this installation already has a PIN set

        :return: True if it does, false otherwise
        """
        data_file = os.getcwd() + Client._LOCAL_DATA_FILE
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                hash = f.readline().strip()
            f.close()

            return len(hash) > 0
        else:
            return False

    @staticmethod
    def verify_pin(username, pin):
        """
        Method to verify the PIN inserted

        :return: True if it is the same as the one saved, false otherwise
        """

        with open(os.getcwd() + Client._LOCAL_DATA_FILE, 'r') as f:
            pin_hash = f.readline().strip()
        f.close()

        return Cryptography.verify_hash(f'{username}:{pin}', pin_hash)

    @staticmethod
    def get_pin():
        """
        Method to get the user's PIN stored in memory

        :return: User's PIN
        """

        return Client._pin

    @staticmethod
    def get_port():
        """
        Method to get the port where the server is listening

        :return: Port used
        """

        return Client._port

    @staticmethod
    def save_message(message):
        """
        Method to persist a message

        :param message: Message to be saved
        """

        file = open(os.getcwd() + Client._LOCAL_DATA_FILE, 'a')
        iv, ciphered_data = Cryptography.cipher(f'{Client.get_pin(): <32}', message)
        file.write(ciphered_data.hex() + '.' + iv.hex() + '\n')
        file.flush()
        file.close()

    @staticmethod
    def set_port(port):
        """
        Method to set the port where connections will be listened

        :param port: Port to be set
        """

        Client._port = port

    @staticmethod
    def start_client():
        """
        Function responsible for running the connections and client bootstrap
        """

        # Creates a connection with the server
        server_connection = Connection.start_server_connection()
        # Listens to the port waiting for clients, for each client, setups a new thread for interaction
        Functionalities.server_functionalities(Client, server_connection)

    @staticmethod
    def listen_for_messages():
        """
        Function responsible for receiving messages
        """

        listening_socket = Connection.start_client_connection(hostname=Client.get_hostname(), port=Client.get_port())
        Connection.accept_connections(listening_socket, Client, Functionalities.receive_messages)
        listening_socket.close()


def main(hostname='127.0.0.1',
         port=8081,
         database_location='/data',
         client_cert='/client.crt',
         client_key='/client.key',
         ca_file='/server.crt'):
    """
    Main thread
    """

    Client.set_hostname(hostname)
    Client.set_port(port)
    Client.set_local_file(database_location)

    Connection.set_ca_file(ca_file)
    Connection.set_cert_file(client_cert)
    Connection.set_key_file(client_key)

    logging.basicConfig(filename='logs.log', level=logging.INFO, filemode='a')
    _thread.start_new_thread(Client.listen_for_messages, ())
    Client.start_client()


if __name__ == '__main__':
    """
    Method to handle the program closing 
    """

    try:
        if len(sys.argv) != 7:
            main()
        else:
            main(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
