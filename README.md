## RUN SERVER
python -m server.server

### RUN CLIENT

python -m client.client <HOSTNAME> <PORT> <DATABASE> <CLIENT_CERT> <CLIENT_KEY> <CA_CERT>

example:

python -m client.client 127.0.0.1 8082 client/data_server2 client/client.crt client/client.key client/server.crt
