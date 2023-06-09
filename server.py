# echo-server.py

import socket
import time
import json

# things to begin with


def Tcp_connect(HostIp, Port):
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HostIp, Port))
    return


def Tcp_server_wait(numofclientwait, port):
    global s2
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2.bind(('', port))
    s2.listen(numofclientwait)


def Tcp_server_next():
    global s
    s = s2.accept()[0]


def Tcp_Write(D):
    mes = str(D + '\r')
    s.send(mes.encode())
    return


def send_file(file_path):
    with open(file_path, 'r') as file:
        file_contents = file.read()
    Tcp_Write(file_contents)


def Tcp_Read():
    a = ' '
    b = ''
    while a != '\r':
        a = s.recv(1).decode()
        b = b + a

    b_dict = eval(b)  # dictionary format
    with open("database/json_received.json", "w") as f:
        json.dump(b_dict, f)
    # return b_dict


def Tcp_Close():
    s.close()
    return


#Tcp_connect('153.19.216.10', 17098)
Tcp_server_wait(5, 17098)
Tcp_server_next()

while True:
    json_data = Tcp_Read()
    send_file('database/board_state_json.json')
    break

Tcp_Close()
