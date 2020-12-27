import socket
import time
import threading
from termcolor import colored, cprint
from _thread import start_new_thread

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
        # booting server all we need for connection
        self.server_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        self.server_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.server_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        thread = threading.Thread(target=self.mannager,args=())
        thread.start()


    def mannager(self):
        # while True:
        self.offer_announcements_udp()
        self.game_mode()

    def game_mode(self):
        print('_______________')
        print('In Game Mode')
        print('_______________')
        pass

    def offer_announcements_udp(self):
        print('_______________')
        print('In Brodcast Mode')
        print('_______________')
        # color text
        cprint(self.booting_message, 'grey', 'on_white')
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
        # print('Close connection')


    # def boot_server(self):
    #     # print message
    #     print(self.booting_message)
    #     self.start_boot_time = time()
    #     while True:
    #         current_time = time()
    #         delta_time = current_time - self.start_boot_time
    #         if delta_time > 15:
    #             break
    #         try:
    #             server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #             server_socket_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #             server_socket_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    #             server_socket_tcp.settimeout(10)