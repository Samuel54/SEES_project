from connection import Connection

# Binds a socket to a specific port
server_socket = Connection.start_socket(hostname='127.0.0.1', port=8080)
# Listens to the port waiting for clients, for each client, setups a new thread for interaction
Connection.accept_connections(server_socket, ())
# Closes the socket when ending everything
server_socket.close()
