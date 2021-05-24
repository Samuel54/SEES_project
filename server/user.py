import json
import logging

from crypto.helpers import Cryptography
from helpers.Random import generate_one_time_id
from server.database.users import Database


class User:
    """
    User inside our system. Composed by:
     - username
     - full name
     - email
     - clearance level
     - one time id
    """

    def __init__(self, full_name, email, username, clearance_level, one_time_id_hash, login_done=False):
        """
        User constructor, initializes a user object

        :param full_name: User's full name
        :param email: User's email
        :param username: User's username, defined by the administrator
        :param clearance_level: User's clearance level, defined by the administrator
        :param one_time_id_hash: User's one time id, system defined
        """

        self.full_name = full_name
        self.email = email
        self.username = username
        self.clearance_level = clearance_level
        self.one_time_id_hash = one_time_id_hash
        self.login_done = login_done

    def get_clearance_level(self):
        """
        Method to get the user's clearance level

        :return: The User's clearance level
        """

        return self.clearance_level

    @staticmethod
    def create():
        """
        Static method to create a new user. This method asks the system administrator for the relevant information

        :return: User's username, User's one time id
        """

        full_name = input('Please insert the User\'s full name: ')
        email = input('Please insert the User\'s email: ')
        username = ''
        username_exists = True
        # Username needs to have 12 characters at most
        while len(username) > 12 or username_exists:
            username = input('Please insert the User\'s username(max of 12 characters): ')
            username_exists = Database.username_exists(username)
            if username_exists:
                print('Username already exists! Please choose another.')
        clearance_level = 0
        # clearance level must be between 1 and 3
        while 1 > clearance_level or clearance_level > 3:
            clearance_level = int(input('Please insert the User\'s clearance level[1-3]: '))

        one_time_id = generate_one_time_id()

        # Creates a new user with all the information
        user = User(full_name, email, username, clearance_level, Cryptography.hash_data(one_time_id))
        # Saves user to the database
        user_data = json.dumps(user.to_dictionary())
        Database.save_user(user.username, user_data)

        return username, one_time_id

    @staticmethod
    def load_user(username):
        """
        Method that loads a given user from the database

        :param username: User's username that will be loaded
        :return: User instance if existent, None otherwise
        """

        data = Database.load_user(username)
        if data is not None:
            user_info = json.loads(data)
            return User(user_info['full_name'],
                        user_info['email'],
                        user_info['username'],
                        user_info['clearance_level'],
                        user_info['one_time_id_hash'],
                        user_info['login_done'],)
        else:
            return None

    def to_dictionary(self):
        """
        Convert User class in a dictionary with only strings to be serialized into json

        :return: Dictionary with all the user's properties
        """

        dictionary = self.__dict__
        if type(dictionary['one_time_id_hash']) == bytes:
            dictionary['one_time_id_hash'] = dictionary['one_time_id_hash'].hex()
        return dictionary

    @staticmethod
    def login(username, one_time_id):
        """
        Method to perform a login of a user

        :param username: User that we want to perform the challenge on
        :param one_time_id: One Time ID passed to perform the login
        :return: True if the username and one time id combination match, false otherwise
        """

        user = User.load_user(username)
        # Checks if a user was found (and hence, is not None), the one time id passed matches with the one stored and
        # did not yet performed any other login with this one time id
        if user is not None and Cryptography.verify_hash(one_time_id, user.one_time_id_hash) and not user.login_done:
            user.login_done = True
            # Save change to the database
            user_data = json.dumps(user.to_dictionary())
            Database.update_user(user.username, user_data)
            return True

        if user is not None and user.login_done:
            logging.debug(f'Login retry on {username}')
        return False
