from termcolor import cprint
from concurrent.futures import ThreadPoolExecutor
from random import randint
from time import *
from socket import *
from threading import *

MAX_BYTE = 2028
FORMAT = 'utf-8'
DISCONNECT_MSG = 'DISCONNECT!'
MAGIC_COOKIE = 'feedbeef'
MESSAGE_TYPE = '02'
WAIT_TIME = 5
DEFAULT_PORT = 13117
NUMBER_OF_CLIENTS = 10
DICT_THEME = {
                'error': ('red', 'on_grey'),
                'connection': ('grey', 'on_magenta'),
                'request': ('magenta', 'on_grey'),
                'disconnect': ('magenta', 'on_white'),
                'game': ('cyan', 'on_grey'),
                'default': ('grey', 'on_white'),
            }

class keyBoardGame:
    
    def __init__(self, NUMBER_OF_CLIENTS = 15, FORAMT='utf-8', MAX_BYTE=2028, game_time=10):
        self.executor = ThreadPoolExecutor(NUMBER_OF_CLIENTS)
        self.groups_clients = {'1': [], '2': []}
        self.client = {}
        self.score = [0,0]
        self.format = FORAMT
        self.game_end_time = 0
        self.game_time = game_time
        self.message_size = MAX_BYTE
        self.number_of_client = NUMBER_OF_CLIENTS
        self.best_player_tuple = (0,'Default') #(score, name)

    def reset(self,NUMBER_OF_CLIENTS = 15):
        self.executor = ThreadPoolExecutor(NUMBER_OF_CLIENTS)
        self.groups_clients = {'1': [], '2': []}
        self.client ={}
        self.score = [0, 0]

    def add_client(self, addr,connection_socket, team_name):
        group_num = randint(1, 2)
        lst = [0, 2, 1]
        if len(self.groups_clients[str(group_num)]) >= len(self.groups_clients[str(lst[group_num])]):
            group_num = lst[group_num]
        # Todo: can delete to have more clients
        # if len(self.groups_clients[str(group_num)]) >= 2:
        #     return False
        self.client[addr[0]] = [addr[1], connection_socket, team_name, group_num]
        if addr[0] not in self.client.keys():
            self.client[addr[0]] = []
        self.groups_clients[str(group_num)].append(team_name)
        return True

    def get_welcome_msg(self):
        group1 = self.groups_clients['1']
        group2 = self.groups_clients['2']
        msg = "Welcome to Keyboard Spamming Battle Royale.\n"
        msg += "Group 1:\n==\n"
        for team1 in group1:
            msg += str(team1) + '\n'
        msg += "Group 2:\n==\n"
        for team2 in group2:
            msg += str(team2) + '\n'
        msg += "Start pressing keys on your keyboard as fast as you can!!"
        return msg

    def start(self):
        self.game_end_time = time() + self.game_time
        for ip, info_list in self.client.items():
            player_socket = info_list[1]
            self.executor.submit(self.start_game_for_player, (ip, player_socket))
        self.executor.shutdown(wait=True)
        self.calculate_group_scores()
        end_msg_byte = self.end_msg().encode(self.format)
        self.executor = ThreadPoolExecutor(self.number_of_client)
        for ip, info_list in self.client.items():
            player_socket = info_list[1]
            self.executor.submit(self.send_end_game_message_to_client, ip,player_socket,end_msg_byte)
        self.executor.shutdown(wait=True)

    def start_game_for_player(self,player):
        player_ip, player_socket = player
        distinct_key_counter = {}
        self.client[player_ip].append(distinct_key_counter)
        player_socket.send(self.get_welcome_msg().encode(self.format))
        while self.game_end_time > time():
            try:
                player_socket.settimeout(self.game_end_time-time())
                key_pressed = str(player_socket.recv(self.message_size).decode(self.format))
                if key_pressed not in distinct_key_counter.keys():
                    distinct_key_counter[key_pressed] = 0
                distinct_key_counter[key_pressed] += 1
            except timeout:
                pass

    def calculate_group_scores(self):
        # Format of {ip: [port, socket, team_name, group_number,dict{'keyPress': counter}]}
        for ip, info_list in self.client.items():
            distinct_key_counter = info_list[4]
            group_number = info_list[3]
            player_sum = sum(distinct_key_counter.values())
            self.score[group_number - 1] += player_sum
            distinct_key_counter.clear()
            if player_sum > self.best_player_tuple[0] or self.best_player_tuple[0] == 0:
                self.best_player_tuple = (player_sum,info_list[2])

    def end_msg(self):
        # Format of {ip: [port, socket, team_name, group_number,dict{'keyPress': counter}]}
        group1_lst = self.score[0]
        group2_lst = self.score[1]
        for ip, info_list in self.client.items():
            client_group_name = info_list[2]
            key_pressed_dict = info_list[3]
            sum_group = []
            if client_group_name == 1:
                sum_group = group1_lst
            elif client_group_name == 2:
                sum_group = group2_lst
            else:
                continue
            sum_group += sum(key_pressed_dict.values())
        message = "Game over! \n"
        message += f"Group 1 typed in {self.score[0]} characters. Group 2 typed in {self.score[1]} characters.\n"
        win_group = '2'
        if self.score[0] > self.score[1]:
            win_group = '1'
        message += win_group + " wins! \n\n"
        message += "Congratulations to the winners:\n==\n"
        for name in self.groups_clients[win_group]:
            message += name + "\n"
        return message + self.statistic()

    def statistic(self):
        msg = f'BEST PLAYER IN THE WORD IS ........ {self.best_player_tuple[1]} \n'
        return msg

    def send_end_game_message_to_client(self,client_ip,client_socket,msg):
        client_socket.send(msg)

class server:

    def print_in_theme(self,msg,kind):
        color = ''
        background = ''
        if kind not in DICT_THEME.keys():
            color, background = DICT_THEME['default']
        else:
            color, background = DICT_THEME[kind]
        cprint(msg, color, background)

    def __init__(self, PORT):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.addr = (gethostbyname(gethostname()), PORT)
        self.udp_lock = Lock()
        self.tcp_lock = Lock()
        self.client_connect_lock = Lock()
        self.game = keyBoardGame(NUMBER_OF_CLIENTS,FORMAT,MAX_BYTE,WAIT_TIME)
        self.connected_client_socket = []
        Thread(target=self.game_manager, args=()).start()

    def game_manager(self):
        while True:
            self.udp_lock.acquire()
            self.tcp_lock.acquire()
            self.print_in_theme(f'Server started, listening on IP address {self.addr[0]}', 'request')
            Thread(target=self.offer_connection_vid_udp, args=()).start()
            self.create_connection_via_tcp()
            self.game.start()
            self.free_all_client_socket()
            self.game.reset(NUMBER_OF_CLIENTS)
            self.print_in_theme("Game over, sending out offer requests...", 'disconnect')

    def offer_connection_vid_udp(self):
        self.udp_lock.acquire()
        self.udp_lock.release()
        udp_socket = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
        udp_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT,1)
        udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST,1)
        udp_socket.settimeout(0.2)
        msg = bytes.fromhex(MAGIC_COOKIE) + bytes.fromhex(MESSAGE_TYPE) + self.addr[1].to_bytes(2, byteorder='big') + self.addr[0].encode(FORMAT)
        self.end_time = time() + WAIT_TIME
        self.tcp_lock.release()
        while self.end_time > time():
            try:
                udp_socket.sendto(msg, ('<broadcast>', DEFAULT_PORT))
            except timeout:
                pass
                if self.end_time - time() < 0:
                    break
                sleep_time = 1 if self.end_time - time() > 1 else self.end_time-time()
                sleep(sleep_time)
        udp_socket.close()

    def create_connection_via_tcp(self):
        tcp_connection = socket(AF_INET, SOCK_STREAM)
        tcp_connection.settimeout(WAIT_TIME)
        tcp_connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        tcp_connection.bind(self.addr)
        tcp_connection.listen()
        self.udp_lock.release()
        self.tcp_lock.acquire()
        self.tcp_lock.release()
        while self.end_time > time():
            try:
                tcp_connection.settimeout(self.end_time - time())
                connection_socket, addr = tcp_connection.accept()
                self.connected_client_socket.append(connection_socket)
                Thread(target=self.when_client_connected,args=(connection_socket, addr,)).start()
            except timeout:
                break
        tcp_connection.close()

    def when_client_connected(self, connection_socket, addr):
        name_msg = connection_socket.recv(MAX_BYTE).decode(FORMAT)
        self.print_in_theme(f"Received offer from {addr[0]},attempting to connect...", 'connection')
        msg_to_client = "#"
        if self.end_time > time():
            self.client_connect_lock.acquire()
            has_joined = self.game.add_client(addr, connection_socket, name_msg)
            self.client_connect_lock.release()
            if not has_joined:
                connection_socket.send(msg_to_client.encode(FORMAT))

    def free_all_client_socket(self):
        for client_socket in self.connected_client_socket:
            client_socket.close()

server(1212)