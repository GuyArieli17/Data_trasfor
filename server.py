#  from termcolor import cprint
from concurrent.futures import ThreadPoolExecutor
from random import randint
from time import *
from socket import *
from threading import *
import scapy.all as scapy
from struct import pack

DEV = 'eth1'
TEST = 'eth2'
MAX_BYTE = 2028
FORMAT = 'utf-8'
DISCONNECT_MSG = 'DISCONNECT!'
# MAGIC_COOKIE = 'feedbeef'
# MESSAGE_TYPE = '02'
WAIT_TIME = 5
SERVER_PORT = 1207  # get free one
DEFAULT_PORT = 13117
NUMBER_OF_CLIENTS = 10
SERVER_IP = gethostbyname(gethostname()) #scapy.get_if_addr(DEV)  # gethostbyname(gethostname())
DICT_THEME = {
    'error': ('red', 'on_grey'),
    'connection': ('grey', 'on_magenta'),
    'request': ('magenta', 'on_grey'),
    'disconnect': ('magenta', 'on_white'),
    'game': ('cyan', 'on_grey'),
    'default': ('grey', 'on_white'),
}

class bcolors:
    """
        Class: we use to print colors need to be in start of end
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class keyBoardGame:
    """
        class: mannage all the game threads and all except sockets server deliver them
    """

    def __init__(self, NUMBER_OF_CLIENTS=15, FORAMT='utf-8', MAX_BYTE=2028, game_time=10):
        """
        the func create the game
        :param NUMBER_OF_CLIENTS: number of thread in thread pool
        :param FORAMT: how we decode\encode str
        :param MAX_BYTE: max message bytes
        :param game_time: how much time the game will be
        """
        self.executor = ThreadPoolExecutor(NUMBER_OF_CLIENTS)
        self.groups_clients = {'1': [], '2': []}  # groups: players in group
        self.client = {}  # client in the game
        self.score = [0, 0]  # the score of each group
        self.format = FORAMT #
        self.game_end_time = 0
        self.game_time = game_time
        self.message_size = MAX_BYTE
        self.number_of_client = NUMBER_OF_CLIENTS
        self.best_player_tuple = (0, 'Default')  # (score, name)

    def reset(self, NUMBER_OF_CLIENTS=15):
        """
            resat the game all score and evrey thing
        :param NUMBER_OF_CLIENTS:
        :return:
        """
        self.executor = ThreadPoolExecutor(NUMBER_OF_CLIENTS)
        self.groups_clients = {'1': [], '2': []}
        self.client = {}
        self.score = [0, 0]

    def add_client(self, addr, connection_socket, team_name):
        """
         add client to our game
        :param addr: the (ip , port) of client
        :param connection_socket:  the socket we diliver msg
        :param team_name: the name of the client
        :return: is in game
        """
        group_num = randint(1, 2)
        lst = [0, 2, 1]
        if len(self.groups_clients[str(group_num)]) >= len(self.groups_clients[str(lst[group_num])]):
            group_num = lst[group_num]
        self.client[addr[0]] = [addr[1], connection_socket, team_name, group_num]
        if addr[0] not in self.client.keys():
            self.client[addr[0]] = []
        self.groups_clients[str(group_num)].append(team_name)
        return True

    def get_welcome_msg(self):
        """
            get teams name and client in each group and print the msg as flollow
        :return:
        """
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
        """
            the msater : manage the game
        :return: None
        """
        self.game_end_time = time() + self.game_time  # set global game end time
        for ip, info_list in self.client.items():  # start game in each thread
            player_socket = info_list[1]
            self.executor.submit(self.start_game_for_player, (ip, player_socket))
        self.executor.shutdown(wait=True)  # wait untill all thread in pool finish (all tasks)
        self.calculate_group_scores() # caculate the score for each group
        end_msg_byte = self.end_msg().encode(self.format) # create message to send to clients
        self.executor = ThreadPoolExecutor(self.number_of_client) # create new thread pool
        for ip, info_list in self.client.items():
            # for each player send the end msg
            player_socket = info_list[1]
            self.executor.submit(self.send_end_game_message_to_client, ip, player_socket, end_msg_byte)
        self.executor.shutdown(wait=True) # wait untill all goot msg

    def start_game_for_player(self, player):
        """
            start the game for each player (in other therads)
        :param player:
        :return:
        """
        player_ip, player_socket = player # get player msg,addr
        distinct_key_counter = {} # create key pressed dict we will work with
        self.client[player_ip].append(distinct_key_counter) # add it to info_list
        player_socket.send(self.get_welcome_msg().encode(self.format)) # sed welcome msg to client
        while self.game_end_time > time(): # run untill global time
            try:
                player_socket.settimeout(self.game_end_time - time())  # set delta time to recv
                key_pressed = str(player_socket.recv(self.message_size).decode(self.format))
                if key_pressed not in distinct_key_counter.keys(): # if we saw the key in user
                    distinct_key_counter[key_pressed] = 0
                distinct_key_counter[key_pressed] += 1 # inc
            except timeout:
                pass

    def calculate_group_scores(self):
        """
            After game over run on all cliets and add to thier team thier point , sum it up
        :return:
        """
        # Format of {ip: [port, socket, team_name, group_number,dict{'keyPress': counter}]}
        for ip, info_list in self.client.items():
            distinct_key_counter = info_list[4]
            group_number = info_list[3]
            player_sum = sum(distinct_key_counter.values())
            self.score[group_number - 1] += player_sum
            distinct_key_counter.clear()
            if player_sum > self.best_player_tuple[0] or self.best_player_tuple[0] == 0: # update best player
                self.best_player_tuple = (player_sum, info_list[2])

    def end_msg(self):
        """
            MSG = all inforamtion about pressed and who wins
            :return: MSG
        """
        group1_lst = self.score[0]
        group2_lst = self.score[1]
        # need to ignore not in use but afrid to delte
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
        """
        :return: string with all statistic we collected
        """
        #  the best player
        msg = f'BEST PLAYER IN THE WORD IS ........ {self.best_player_tuple[1]} \n'
        return msg

    def send_end_game_message_to_client(self, client_ip, client_socket, msg):
        client_socket.send(msg)

class server:
    """
        The class accept deniyu add users
    """
    def print_in_theme(self, msg, kind):
        """
            We did in a cool way but afried it will not work (run in server all good)
            pritn color text by ,msg
        """
        #betters colors
        color = ''
        background = ''
        # if kind not in DICT_THEME.keys():
        #     color, background = DICT_THEME['default']
        # else:
        #     color, background = DICT_THEME[kind]
        # cprint(msg, color, background)
        print(f'{bcolors.OKCYAN} {msg}{bcolors.ENDC}')

    def __init__(self):
        """
            init all information for the server
        """
        self.socket = socket(AF_INET, SOCK_STREAM) # create socket
        self.addr = (SERVER_IP, SERVER_PORT) # our defualt addr
        # loocks we will use for threads
        self.udp_lock = Lock()
        self.tcp_lock = Lock()
        self.client_connect_lock = Lock()
        # create the game
        self.game = keyBoardGame(NUMBER_OF_CLIENTS, FORMAT, MAX_BYTE, WAIT_TIME)
        self.connected_client_socket = []
        # start server (we dont block main thread)
        Thread(target=self.game_manager, args=()).start()

    def game_manager(self):
        """
            run untill server close
            print all coneection and send offer by udp
            create connection in tcp
            begin game
            sum score
            send client msg
            re-do
        :return:
        """
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
        """
            send all my port and ip to connect
        :return:
        """
        self.udp_lock.acquire()
        self.udp_lock.release()
        # create udp socket
        udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        udp_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        # set time so we will not get stuck (no need)
        udp_socket.settimeout(0.2)
        # bind the pysical socket with this addr
        udp_socket.bind((SERVER_IP, SERVER_PORT))
        # set new addr as os createed (change the port)
        self.addr = udp_socket.getsockname()
        msg = pack('!IbH', 0xfeedbeef, 2, self.addr[1]) # send client my connection port
        self.end_time = time() + WAIT_TIME # set global wait time
        self.tcp_lock.release()# tcp can bigin
        while self.end_time > time(): # run untill time over
            try:
                udp_socket.sendto(msg, ('<broadcast>', DEFAULT_PORT)) #172.1.255.255
            except timeout:
                pass
            if self.end_time - time() < 0:
                break
            sleep_time = 1
            if self.end_time - time() < 1:
                sleep_time = self.end_time - time()
            sleep(sleep_time)
        udp_socket.close()

    def create_connection_via_tcp(self):
        """
            Create the TCP coonection
        :return: None
        """
        # create tcp connection
        tcp_connection = socket(AF_INET, SOCK_STREAM)
        tcp_connection.settimeout(WAIT_TIME)
        tcp_connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # bind socket with addr
        tcp_connection.bind(self.addr)
        # st listing to clients
        tcp_connection.listen()
        self.udp_lock.release() # udp can start running
        self.tcp_lock.acquire() # tcp need to be realse by udp
        self.tcp_lock.release() # free for next run
        while self.end_time > time(): # run on global time
            try:
                tcp_connection.settimeout(self.end_time - time())
                connection_socket, addr = tcp_connection.accept()
                self.connected_client_socket.append(connection_socket)
                Thread(target=self.when_client_connected, args=(connection_socket, addr,)).start()
            except timeout:
                break
        tcp_connection.close()

    def when_client_connected(self, connection_socket, addr):
        """
            new thread we accept clients and handle them
        :param connection_socket:
        :param addr:
        :return:
        """
        name_msg = connection_socket.recv(MAX_BYTE).decode(FORMAT) #  client name
        self.print_in_theme(f"Received offer from {addr[0]},attempting to connect...", 'connection')
        msg_to_client = "#" # on error (Max player no need)
        if self.end_time > time(): # global time
            self.client_connect_lock.acquire()
            has_joined = self.game.add_client(addr, connection_socket, name_msg)
            self.client_connect_lock.release()
            if not has_joined:
                connection_socket.send(msg_to_client.encode(FORMAT))

    def free_all_client_socket(self):
        """
            run on all clients socket and free them before next run
        :return:
        """
        for client_socket in self.connected_client_socket:
            client_socket.close()


server()