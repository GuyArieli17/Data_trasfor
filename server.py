import socket
import time
import threading
from random import random

from termcolor import colored, cprint
from _thread import start_new_thread
from threading import Lock

class server:

    def __init__(self,NAME,IP,PORT,broadcast_port = 13117):
        """
        :param NAME: the name fo the server
        :param IP: ip of the server
        :param PORT: the port we will use to brodcast (use in the future)
        """
        #all parms from arg - save in self
        self.server_name = NAME
        self.server_ip = IP
        self.server_port = PORT
        self.broadcast_port = broadcast_port
        # information we will print
        self.booting_message = "Server started, listening on IP address " + str(self.server_ip)
        # resat number of client to zero(just started the server)
        self.num_of_client = 0
        # create a lock we will use
        self.lock = Lock()
        # booting server all we need for connection
        thread = threading.Thread(target=self.mannager,args=())
        thread.start()

    def handle_client(self,data):
        # get the data from the client(is team name)
        client_team_name = str(data.recv(1024), 'utf-8')
        # Todo: send game info to user
        # Todo: add all user game
        pass

    def game_mode(self):
        print('_______________')
        print('In Game Mode')
        print('_______________')
        while True:
            # establish connection with client
            data, addr = self.tcp_connection_socket.accept()
            self.lock.acquire()
            #inc number of particants
            self.num_of_client += 1
            self.lock.release()
            # Start a new thread and return its identifier
            start_new_thread(self.handle_client, (data,))


    def offer_announcements_udp(self):
        print('_______________')
        print('In Brodcast Mode')
        print('_______________')
        # get time when started brodacsting
        start_listining_time = time.time()
        current_time =start_listining_time
        self.bordcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Enable port reusage
        self.bordcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # Enable broadcasting mode
        self.bordcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Set a timeout so the socket does not block
        self.bordcast_socket.settimeout(0.2)
        # the magic_cookie we will check the client really want to connect (kind of message)
        magic_cookie = "feedbeef"
        # the kind of the massage (connection) offer
        message_type = "02"
        # convert all message to byte
        magic_cookie_bytes = bytes.fromhex(magic_cookie)
        message_type_bytes = bytes.fromhex(message_type)
        server_port_bytes = self.server_port.to_bytes(2, byteorder='big')
        # combaine all the message in bye as ordered
        message = magic_cookie_bytes + message_type_bytes + server_port_bytes
        # run for 10 sec
        while current_time - start_listining_time < 10:
            # evrey secound ~ send bordcast
            self.bordcast_socket.sendto(message, ('<broadcast>', self.broadcast_port))
            time.sleep(1)
            # get current time
            current_time = time.time()
        #end the connection
        self.bordcast_socket.close()
        # print('Close connection')

    def mannager(self):
        # create tcp connection to client to join
        self.tcp_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_connection_socket.bind((self.server_ip, self.server_port))
        # color text
        cprint(self.booting_message, 'grey', 'on_white')
        thread = threading.Thread(target=self.offer_announcements_udp)
        thread.start()
        self.tcp_connection_socket.listen(4)
        self.game_mode()
