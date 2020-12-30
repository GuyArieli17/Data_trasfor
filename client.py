from socket import *
from termcolor import cprint
from threading import *
from getch import *
import sys
from select import select

MAX_BYTE = 2028
FORMAT = 'utf-8'
DISCONNECT_MSG = 'DISCONNECT!'
DEFAULT_PORT = 13113
MAGIC_COOKIE = 'feedbeef'
DICT_THEME = {
                'error': ('red', 'on_grey'),
                'connection': ('grey', 'on_magenta'),
                'request': ('magenta', 'on_grey'),
                'disconnect': ('grey', 'on_red'),
                'game': ('cyan', 'on_grey'),
                'default': ('grey', 'on_white'),
            }

class client:

    def print_in_theme(self,msg,kind):
        color = ''
        background = ''
        if kind not in DICT_THEME.keys():
            color, background = DICT_THEME['default']
        else:
            color, background = DICT_THEME[kind]
        cprint(msg, color, background)

    def __init__(self, PORT, NAME):
        self.addr = (gethostbyname(gethostname()),PORT)
        self.name = NAME
        self.waiting_lock = Lock()
        Thread(target=self.wait_for_connection_offer,args=()).start()

    def wait_for_connection_offer(self):
        udp_socket = socket(AF_INET,SOCK_DGRAM)
        udp_addr = ('',DEFAULT_PORT)
        udp_socket.bind(udp_addr)
        self.print_in_theme("Client started, listening for offer requests...", 'request')
        msg_byte, addr = udp_socket.recvfrom(MAX_BYTE)
        magic_cookie = msg_byte[:4].hex()
        if magic_cookie == MAGIC_COOKIE:
            tcp_port_byte = msg_byte[5:7]
            ip_tcp_bytes = msg_byte[7:]
            ip_tcp = ip_tcp_bytes.decode('utf8')
            # convert to int (can work with)
            tcp_port = int.from_bytes(tcp_port_byte, byteorder='big', signed=False)
            udp_socket.close()
            self.connect_via_tcp((ip_tcp, tcp_port))
        else:
            udp_socket.close()
            self.wait_for_connection_offer()

    def connect_via_tcp(self, server_addr):
        con_bol = True
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        try:
            tcp_socket.connect(server_addr)
        except:
            tcp_socket.close()
            return
        tcp_socket.send(self.name.encode(FORMAT))
        try:
            welcome_msg = tcp_socket.recv(MAX_BYTE).decode(FORMAT)
            if welcome_msg == '#':
                self.print_in_theme("Can't connect to server - too many players...", 'error')
            else:
                # Todo: config time
                self.print_in_theme(welcome_msg,'game')
                capture_thread = Thread(target=self.capture_keys, args=(tcp_socket,))
                capture_thread.start()
                end_msg = tcp_socket.recv(MAX_BYTE).decode(FORMAT)
                self.waiting_lock.release()
                self.print_in_theme(end_msg, 'game')

        except timeout:
            pass
        self.wait_for_connection_offer()
        tcp_socket.close()

    def kbhit(self):
        dr, dw, de = select([sys.stdin], [], [], 0)
        return dr != []

    def capture_keys(self,socket):
        self.waiting_lock.acquire()
        # fd = sys.stdin.fileno()
        # old_settings = termios.tcgetattr(fd)
        while self.waiting_lock.locked():
            # input_key = sys.stdin.read(1)
            # if input_key == '\n'
            # input_key = input()
            try:
                if not self.kbhit():
                    continue
                input_key = getche()
                socket.send(input_key.encode(FORMAT))
            except:
                pass
            

client(13117, 'Vladimir Computin')
