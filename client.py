from socket import *
from termcolor import cprint
from threading import *
from getch import *
import sys
from select import select
from struct import *
from concurrent.futures import ThreadPoolExecutor
from time import *
from threading import *
import scapy.all as scapy

DEV = 'eth1'
TEST = 'eth2'
MAX_BYTE = 2028
FORMAT = 'utf-8'
DISCONNECT_MSG = 'DISCONNECT!'
DEFAULT_PORT = 13117
SERVER_IP = scapy.get_if_addr(TEST)#'172.1.0.107'
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

    def print_in_theme(self, msg, kind):
        color = ''
        background = ''
        if kind not in DICT_THEME.keys():
            color, background = DICT_THEME['default']
        else:
            color, background = DICT_THEME[kind]
        cprint(msg, color, background)

    def _init_(self, PORT, NAME):
        self.addr = (SERVER_IP, PORT) #gethostbyname(gethostname())
        self.name = NAME
        self.waiting_lock = Lock()
        self.closing_lock = Lock()
        Thread(target=self.wait_for_connection_offer, args=()).start()

    def wait_for_connection_offer(self):
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_addr = ('', DEFAULT_PORT)
        udp_socket.bind(udp_addr)
        self.print_in_theme("Client started, listening for offer requests...", 'request')
        finsih_loop = False
        while not finsih_loop:
            msg_byte, addr = udp_socket.recvfrom(MAX_BYTE)
            try:
                magic_cookie, message_type, tcp_port = unpack('!IbH', msg_byte)
                if magic_cookie == MAGIC_COOKIE and message_type == MESSAGE_TYPE:
                    finsih_loop = True
                    udp_socket.close()
                    self.connect_via_tcp((addr[0], tcp_port))
            except Exception as e:
                pass

    def connect_via_tcp(self, server_addr):
        con_bol = True
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        try:
            print(f'[Client] connection time {time()}')
            tcp_socket.connect(server_addr)
        except Exception as e:
            print(e)
            tcp_socket.close()
            self.wait_for_connection_offer()

        tcp_socket.send(self.name.encode(FORMAT))
        try:
            welcome_msg = tcp_socket.recv(MAX_BYTE).decode(FORMAT)
            if welcome_msg == '#':
                self.print_in_theme("Can't connect to server - too many players...", 'error')
            else:
                self.print_in_theme(welcome_msg, 'game')
                capture_thread = Thread(target=self.capture_keys, args=(tcp_socket,))
                capture_thread.start()
                end_msg = tcp_socket.recv(MAX_BYTE).decode(FORMAT)
                self.closing_lock.acquire()
                self.waiting_lock.release()
                self.print_in_theme(end_msg, 'game')
        except timeout:
            pass
        tcp_socket.close()
        self.wait_for_connection_offer()

    def kbhit(self):
        dr, dw, de = select([sys.stdin], [], [], 0)
        return dr != []

    def capture_keys(self, socket):
        self.waiting_lock.acquire()
        while self.waiting_lock.locked():
            try:
                if not self.kbhit():
                    continue
                input_key = getche()
                socket.send(input_key.encode(FORMAT))
            except:
                pass
            sleep(0.01)
        self.closing_lock.release()


client(13117, 'Vladimir Computin')