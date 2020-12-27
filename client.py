import socket
import struct
import sys
import threading
from _thread import start_new_thread
from termcolor import cprint

magic_cookie = 0xfeedbeef
offer_msg_type = 0x2
BUFFER_SIZE = 2048
port = 13117

class client:
    def __init__(self,IP,PORT,TEAM_NAME = 'BRAVO'):
        """
        :param server_name:
        :param server_ip:
        :param server_port:
        """
        # self.server_name = server_name
        self.team_name = TEAM_NAME
        self.server_port = PORT
        self.server_ip = IP
        self.listen_message = "Client started, listening for offer requests..."
        start_new_thread(self.listen_to_broadcast,())

    def create_tcp_connection(self,tcp_port):
        # create TCP connection with server
        self.client_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket_tcp.connect((self.server_ip, tcp_port))
        # send message as byte to server (has the name of the team) use utf8
        self.client_socket_tcp.send(bytes(self.team_name, encoding='utf8'))
        # convert the data we got from the server (all the other team and all info)
        data = str(self.client_socket_tcp.recv(1024), 'utf-8')
        # print all the info
        cprint(data, 'red', 'on_white', attrs=['bold'])
        # Todo: need to add the application what to do with client
        self.client_socket_tcp.close()

    def listen_to_broadcast(self):
        """
        :return:
        """
        # create socket
        self.client_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # bind socket with addr ('',port_num)
        self.client_socket_udp.bind(('', port))
        # print message
        cprint(self.listen_message,'white', 'on_grey')
        # get data, addr from server
        data, addr = self.client_socket_udp.recvfrom(1024)
        # strip all from data
        magic_cookie_byte = data[:4]
        message_type_byte = data[4]
        tcp_port_byte = data[5:]
        # convert to int (can work with)
        magic_cookie = int.from_bytes(magic_cookie_byte, byteorder='big', signed=False)
        tcp_port = int.from_bytes(tcp_port_byte, byteorder='big', signed=False)
        # print all info
        print('Magic Cookie: ' + str(magic_cookie))
        print('Message Type: ' + str(message_type_byte))
        print('Port: ' + str(tcp_port))
        print('Team Name: ' + self.team_name)
        # call create tcp connection
        self.create_tcp_connection(tcp_port)
