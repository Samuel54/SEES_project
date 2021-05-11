import socket
import os
from _thread import *
import ssl


####
def multi_threaded_client(connection):
    print("antes")
    connection.send(str.encode('Server is working:'))
    print("depois")
    while True:
        data = connection.recv(2048)
        response = 'Server message: ' + data.decode('utf-8')
        if not data:
            break
        connection.sendall(str.encode(response))
    connection.close()


######
# Define the ssl context parameters
server_cert = 'server.crt'
server_key = 'server.key'
client_certs = 'client.crt'

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=client_certs)

host = '127.0.0.1'
port = 12334
ThreadCount = 0

ServerSideSocket = socket.socket()
try:
    ServerSideSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Socket is listening..')
ServerSideSocket.listen(5)

while True:
    Client, address = ServerSideSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))

    secure_connection = context.wrap_socket(Client, server_side=True)
    print("SSL established. Peer: {}".format(secure_connection.getpeercert()))

    start_new_thread(multi_threaded_client, (secure_connection,))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSideSocket.close()
