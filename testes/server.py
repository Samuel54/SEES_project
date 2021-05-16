#!/usr/bin/python3
"""Multi-Thread server with Perfect Forward Secrecy"""
import socket
import os
from _thread import *
import ssl
import auxLib


####
def multi_threaded_client(connection):
    # Counter for sent and received messages
    count_send = 0
    count_recv = 0
    message = str('Server is working:').encode('utf-8')
    count_send = auxLib.send_message(connection, message, count_send)

    while True:
        message, count_recv = auxLib.receive_message(connection, count_recv)
        print(message.decode('utf-8'))
        message = 'Server message: ' + message.decode('utf-8')
        message = message.encode('utf-8')
        if not message:
            break
        count_send = auxLib.send_message(connection, message, count_send)
    connection.close()


######
# Create the pre-register file
auxLib.make_user_pre_register()

######
# Define the ssl context parameters
server_cert = 'server.crt'
server_key = 'server.key'
client_certs = 'client.crt'

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=client_certs)
context.set_ecdh_curve('prime256v1')  # Perfect forward secrecy

host = '127.0.0.1'
port = 12334
ThreadCount = 0

ServerSideSocket = socket.socket()
ServerSideSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
