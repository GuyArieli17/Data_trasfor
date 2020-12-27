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
broadcast_address = ('255.255.255.255', port)
team_name = b"IDO ROM <3"
id = 0

class client:
    def __init__(self,IP,PORT):
        """
        :param server_name:
        :param server_ip:
        :param server_port:
        """
        # self.server_name = server_name
        self.server_port = PORT
        self.server_ip = IP
        self.listen_message = "Client started, listening for offer requests..."
        start_new_thread(self.listen_to_broadcast,())

    def create_tcp_connection(self):
        pass

    def listen_to_broadcast(self):
        """
        :return:
        """
        # create socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # bind socket with addr ('',port_num)
        self.client_socket.bind(('', port))
        # print message
        cprint(self.listen_message,'white', 'on_grey')
        # get data, addr from server
        data, addr = self.client_socket.recvfrom(1024)
        # strip all from data
        magic_cookie_byte = data[:4]
        message_type_byte = data[4]
        port_tcp_byte = data[5:]
        # convert to int (can work with)
        magic_cookie = int.from_bytes(magic_cookie_byte, byteorder='big', signed=False)
        port_num = int.from_bytes(port_tcp_byte, byteorder='big', signed=False)
        # print all info
        print('Magic Cookie: ' + str(magic_cookie))
        print('Message Type: ' + str(message_type_byte))
        print('Port: ' + str(port_num))
        # call create tcp connection
        self.create_tcp_connection()
