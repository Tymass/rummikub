# echo-client.py

import socket


# create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get the local machine name
host = socket.gethostname()
port = 12345

# connect to the server
client_socket.connect((host, port))
print('Connected to {}:{}'.format(host, port))

# continuously send and receive data with the server
while True:
    # send data to the server
    message = input('Enter a message to send to server: ')
    client_socket.send(message.encode())

    # receive data from the server
    #data = client_socket.recv(1024)
    #print('Received data from server: {}'.format(data.decode()))

# close the connection
client_socket.close()
