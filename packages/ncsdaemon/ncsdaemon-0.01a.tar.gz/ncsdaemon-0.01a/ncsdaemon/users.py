""" module for user management stuff """
import json
import logging
from ncsdaemon.crypt import Crypt

class User(object):
    """ Class that contains data and operations related to a user """

    def __init__(self, username, first_name, last_name, email, salt, hashed_password, token):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.salt = salt
        self.hashed_password = hashed_password
        self.token = token

    def to_dictionary(self):
        """ Returns the user as a dictionary for easy write to JSON """
        return { 'username' : self.username,
                 'first_name': self.first_name,
                 'last_name': self.last_name,
                 'email': self.email,
                 'salt': self.salt,
                 'hashed_password': self.hashed_password,
                 'token': self.token}

class UserManager(object):
    """ Class that handles users """

    USERS_FILENAME = 'users.json'

    def __init__(self):
        user_dict = self.load_users_file(self.USERS_FILENAME)
        self.users = self.convert_users_dict(user_dict)

    def load_users_file(self, filename):
        """ Loads the JSON formatted users file and
        returns a dictionary that contains the data """
        try:
            with open(filename) as f:
                try:
                    data = f.read()
                    return json.loads(data)
                except ValueError:
                    logging.error('Users file not found or poorly formatted')
        except IOError:
            logging.warning('Users file not found, creating new one')
            user_dict = { 'users': [] }
            with open(filename, 'w') as f:
                f.write(json.dumps(user_dict))
            return user_dict

    def create_user(self, username, first_name, last_name, email, password):
        salt = Crypt.generate_salt()
        hashed_password = Crypt.hash_password(password, salt)
        token = Crypt.generate_user_token()
        user = User(username, first_name, last_name, email, salt, hashed_password, token)
        self.users.append(user)
        self.save_users_file(self.USERS_FILENAME)

    def verify_user(self, username, password):
        """ Verifies that a users password """
        for user in self.users:
            if user.username == username:
                hashed_password = Crypt.hash_password(password, user.salt)
                if hashed_password == user.hashed_password:
                    return True
                else:
                    return False
        return False

    def get_user_token(self, username):
        """ Gets the users token """
        user = self.get_user_by_username(username)
        return user.token

    def save_users_file(self, filename):
        try:
            with open(filename, 'w') as f:
                users = []
                for user in self.users:
                    users.append(user.to_dictionary())
                user_dict = { 'users': users }
                f.write(json.dumps(user_dict))
        except IOError:
            logging.error('Couldn\'t write to users file')

    def convert_users_dict(self, user_dict):
        users = []
        try:
            for user in user_dict['users']:
                users.append(User(user['username'],
                                  user['first_name'],
                                  user['last_name'],
                                  user['email'],
                                  user['salt'],
                                  user['hashed_password'],
                                  user['token']))
            return users
        except KeyError:
            logging.error('Attribute validation of users object failed, check the file')

    def get_user_from_token(self, token):
        for user in self.users:
            if user.token == token:
                return user
        raise KeyError()

    def get_user_by_username(self, username):
        for user in self.users:
            if user.username == username:
                return user
        raise KeyError()


