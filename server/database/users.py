import base64
import os
from os import getcwd

from crypto.helpers import Cryptography


class Database:
    """
    User Database. Used to save, update and load users.
    """

    __DB_FILENAME = "/user_registry"
    __key_file = getcwd() + 'server.py'

    @staticmethod
    def save_user(username, data):
        """
        Method to save a user into the database

        :param username: Username used as the index
        :param data: Data to be saved
        """

        hashed_username = base64.b64encode(Cryptography.hash(username).digest()).decode()

        file = open(getcwd() + Database.__DB_FILENAME, 'a')
        iv, ciphered_data = Cryptography.cipher(Cryptography.get_passphrase(), data)
        file.write(hashed_username + ':' + ciphered_data.hex() + '.' + iv.hex() + '\n')
        file.flush()
        file.close()

    @staticmethod
    def update_user(username, data):
        """
        Method to update a user from the database

        :param username: Username that targets the user to be updated
        :param data: Data to be saved
        """

        hashed_username = base64.b64encode(Cryptography.hash(username).digest()).decode()

        with open(getcwd() + Database.__DB_FILENAME) as file_input,\
                open(getcwd() + Database.__DB_FILENAME + '.temp', 'w') as file_output:
            for entry in file_input:
                new_entry = entry
                if entry.split(':')[0] == hashed_username:
                    iv, ciphered_data = Cryptography.cipher(Cryptography.get_passphrase(), data)
                    new_entry = hashed_username + ':' + ciphered_data.hex() + '.' + iv.hex() + '\n'
                file_output.write(new_entry)
            if os.path.exists(getcwd() + Database.__DB_FILENAME):
                os.remove(getcwd() + Database.__DB_FILENAME)
                os.rename(getcwd() + Database.__DB_FILENAME + '.temp', getcwd() + Database.__DB_FILENAME)

    @staticmethod
    def load_user(username):
        """
        Method to load a user information given a username

        :param username: User's username to be be loaded
        :return: User's information
        """

        hashed_username = base64.b64encode(Cryptography.hash(username).digest()).decode()

        with open(getcwd() + Database.__DB_FILENAME, 'r') as f:
            for entry in f:
                parts = entry.split(':')
                if parts[0] == hashed_username:
                    material = parts[1].split('.')
                    ciphertext = bytearray.fromhex(material[0])
                    iv = bytearray.fromhex(material[1])
                    return Cryptography.decipher(Cryptography.get_passphrase(), ciphertext, iv)
        f.close()
        return None

    @staticmethod
    def username_exists(username):
        """
        Method to check if a user exists in the database

        :param username: Username whose existence will be check
        :return: True if the user with that username exists, False otherwise
        """

        hashed_username = base64.b64encode(Cryptography.hash(username).digest()).decode()

        if os.path.exists(getcwd() + Database.__DB_FILENAME):
            with open(getcwd() + Database.__DB_FILENAME, 'r') as f:
                for entry in f:
                    parts = entry.split(':')
                    if parts[0] == hashed_username:
                        return True
                return False
        else:
            return False
