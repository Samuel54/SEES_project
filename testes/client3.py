import socket
import ssl

# Define the ssl context parameters
server_sni_hostname = 'example.com'
server_cert = 'server.crt'
client_cert = 'client.crt'
client_key = 'client.key'

host = '127.0.0.1'
port = 12334

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)

ClientMultiSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print('Waiting for connection response')
try:
    # ClientMultiSocket.connect((host, port))
    secure_connection = context.wrap_socket(ClientMultiSocket, server_side=False, server_hostname=server_sni_hostname)
    secure_connection.connect((host, port))
except socket.error as e:
    print(str(e))

res = secure_connection.recv(1024)
print(res.decode('utf-8'))

while True:
    Input = input('Hey there: ')
    secure_connection.send(str.encode(Input))
    res = secure_connection.recv(1024)
    print(res.decode('utf-8'))

secure_connection.close()