# echo-client.py

import socket
import time
import json


class Client:
    def __init__(self, host_ip, port):
        self.host_ip = host_ip
        self.port = port

    def read_json_file(self, file_name):
        f = open(file_name)
        # returns JSON object as
        # a dictionary
        data = str(json.load(f))

        print(data)
        return data

    def Tcp_connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host_ip, self.port))
        return

    def Tcp_Write(self, D):
        mes = str(D + '\r')
        self.s.send(mes.encode())
        return

    def Tcp_Read(self):
        a = ' '
        b = ''
        while a != '\r':
            a = self.s.recv(1).decode()
            b = b + a
        return b

    def Tcp_Close(self):
        self.s.close()
        return


client = Client('153.19.216.10', 17098)
client.Tcp_connect()

data = client.read_json_file('database/board_state_json.json')

client.Tcp_Write(data)
print(client.Tcp_Read())
client.Tcp_Write('server')
print(client.Tcp_Read())

client.Tcp_Close()
