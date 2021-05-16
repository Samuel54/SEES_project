from connection import Connection
from crypto.helpers import Cryptography
from user import User


def test():
    Cryptography.set_passphrase("This is secure passphrase to AES")
    username, one_time_id = User.create()
    user = User.load_user(username)
    print('Has login happened? ' + str(user.login_done))
    result = User.login(username, one_time_id)
    print('Login successful: ' + str(result))
    print('User ' + user.username + ' has done the login!')
    user = User.load_user(username)
    print('Has login happened? ' + str(user.login_done))
    result = User.login(username, one_time_id)
    print('Login successful: ' + str(result))
    print('User ' + user.username + ' reused the one time id!')


# Test function just to check the database
test()

# Binds a socket to a specific port
server_socket = Connection.start_socket(hostname='127.0.0.1', port=8080)
# Listens to the port waiting for clients, for each client, setups a new thread for interaction
Connection.accept_connections(server_socket, ())
# Closes the socket when ending everything
server_socket.close()
