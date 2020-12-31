from socket import *
#  from termcolor import cprint
from threading import *
from getch import *
import sys
from select import select
from struct import *
import scapy.all as scapy

DEV = 'eth1'
TEST = 'eth2'
MAX_BYTE = 2028
FORMAT = 'utf-8'
DISCONNECT_MSG = 'DISCONNECT!'
DEFAULT_PORT = 13117
SERVER_IP = scapy.get_if_addr(TEST) #gethostbyname(gethostname()) #
MAGIC_COOKIE = 0xfeedbeef
MESSAGE_TYPE = 2
DICT_THEME = {
    'error': ('red', 'on_grey'),
    'connection': ('grey', 'on_magenta'),
    'request': ('magenta', 'on_grey'),
    'disconnect': ('grey', 'on_red'),
    'game': ('cyan', 'on_grey'),
    'default': ('grey', 'on_white'),
}
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class client:
    """
        class of user
        waits to connection
        establish connection and so on.....
    """
    def print_in_theme(self, msg, kind):
        """
            Same as server want to do cool way but no risk so....
        :param msg: the msg we want to send
        :param kind:
        :return:
        """
        # color = ''
        # background = ''
        # if kind not in DICT_THEME.keys():
        #     color, background = DICT_THEME['default']
        # else:
        #     color, background = DICT_THEME[kind]
        # cprint(msg, color, background)
        print(f'{bcolors.OKCYAN} {msg}{bcolors.ENDC}')

    def __init__(self, PORT, NAME):
        """
        create the client in a new thread
        :param PORT:
        :param NAME:
        """
        self.addr = (SERVER_IP, PORT) # create client addr
        self.name = NAME # name of client
        self.waiting_lock = Lock()
        self.closing_lock = Lock()
        Thread(target=self.wait_for_connection_offer, args=()).start()

    def wait_for_connection_offer(self):
        """
            wait for server to send instruction to new tcp connection by broadcast
        :return:
        """
        # create and bind udp socket
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_addr = ('', DEFAULT_PORT)
        udp_socket.bind(udp_addr)
        self.print_in_theme("Client started, listening for offer requests...", 'request')
        finsih_loop = False
        while not finsih_loop: # run untill found connection or end
            msg_byte, addr = udp_socket.recvfrom(MAX_BYTE) # get msg and from where
            try:
                magic_cookie, message_type, tcp_port = unpack('!IbH', msg_byte) # un pack and get info
                # check if the right msg
                if magic_cookie == MAGIC_COOKIE and message_type == MESSAGE_TYPE:
                    finsih_loop = True
                    udp_socket.close()
                    self.connect_via_tcp((addr[0], tcp_port)) # create tcp connection
            except Exception as e:
                pass
        # self.wait_for_connection_offer()

    def connect_via_tcp(self, server_addr):
        """
        create the tcp connection
        :param server_addr: the server _addr with all info (ip,port)
        :return:
        """
        con_bol = True
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        try:
            tcp_socket.connect(server_addr)
        except Exception as e:  # probbly connection erorr
            print(e)
            tcp_socket.close()
            self.wait_for_connection_offer()  # start again
            # return
        try:
            tcp_socket.send(self.name.encode(FORMAT))  # send my name to server
            welcome_msg = tcp_socket.recv(MAX_BYTE).decode(FORMAT)  # decode welcome msg
            if welcome_msg == '#':  # if server throw us
                self.print_in_theme("Can't connect to server - too many players...", 'error')
            else:  # connecteed to the server
                self.print_in_theme(welcome_msg, 'game')  # pritn the msg
                capture_thread = Thread(target=self.capture_keys, args=(tcp_socket,))
                capture_thread.start()  # start new thread to capture keys
                end_msg = tcp_socket.recv(MAX_BYTE).decode(FORMAT)  # wait to end msg
                self.closing_lock.acquire() #
                self.waiting_lock.release() # realse capture thread
                self.print_in_theme(end_msg, 'game') # print game over
        except timeout:
            pass
        # close all and start over
        tcp_socket.close()
        self.wait_for_connection_offer()

    def kbhit(self):
        """
            see if anything change and dont stop the thread (if typed)
        :return:
        """
        dr, dw, de = select([sys.stdin], [], [], 0)
        return dr != []

    def capture_keys(self, socket):
        """
        send keys to server wait untill get end msg
        :param socket: we will send keys to
        :return:
        """
        self.waiting_lock.acquire()  # so we no when we are relased
        while self.waiting_lock.locked():  #
            try:
                if not self.kbhit():
                    continue
                input_key = getche()
                socket.send(input_key.encode(FORMAT))
            except:
                pass
        self.closing_lock.release()

client(13117, 'Vladimir Computin')
