import socket
import _thread
import time
import random
import json
#from client import Client


class Server:
    MAX_TALK_SIZE = 2048

    def __init__(self, server_name, server_ip, server_port):
        self.server_name = server_name
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_dict = {}  # Format of {ip: [port, socket, team_name, group_number]}
        self.groups = {'Group 1': [], 'Group 2': []}
        self.counters = [0, 0]  # group1, group2 counters
        self.start_time = 0

    def startServer(self):
        print(f"Server started, listening on IP address {self.server_ip}")
        _thread.start_new_thread(self.broadcast_sending())
        _thread.start_new_thread(self.tcp_connection())

    def broadcast_sending(self):
        while len(self.client_dict) < 4:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
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
            server_socket.sendto(message, ('<broadcast>', 13117))
            time.sleep(1)
        self.start_time = time.time()

    def tcp_connection(self):
        self.server_socket.listen(self.server_port)
        steps = 0
        start_time = 0
        while True:
            connection_socket, (ip, port) = self.server_socket.accept()
            if steps == 0:  # start the tcp connection
                print(f"Received offer from {ip},attempting to connect...")
                client = Client(ip, port, connection_socket)
                self.client_list[ip] = list()
                self.client_list[ip].append(port)
                self.client_list[ip].append(connection_socket)
                message = "Type your team name:\n"
                connection_socket.send(message)
                steps += 1
            if steps == 1:  # get the team name
                team_name = connection_socket.recv(self.MAX_TALK_SIZE)[:-1]  # [:-1] remove the \n
                self.client_list[ip].append(team_name)
                self.add_to_random_group(ip, team_name)
                now_time = time.time()
                while now_time - self.start_time < 10:
                    pass  # wait
                start_time = self.start_game()
                # start game and countering the amount of keys of each group
                while time.time() - start_time < 10:
                    self.update_counters(connection_socket, ip)
                print(self.end_game())
            self.disconnect_client()
            connection_socket.close()
        self.server_socket.close()

    def add_to_random_group(self, ip, team_name):
        group_num = random.randint(1, 3)
        if group_num == 1:
            if len(self.groups[f'Group {group_num}']) < 2:
                self.groups['Group 1'].append(team_name)
                self.client_dict[ip].appeand(1)
            else:
                self.groups['Group 2'].append(team_name)
                self.client_dict[ip].appeand(2)
        else:
            if len(self.groups[f'Group {group_num}']) < 2:
                self.groups['Group 2'].append(team_name)
                self.client_dict[ip].appeand(2)
            else:
                self.groups['Group 1'].append(team_name)
                self.client_dict[ip].appeand(1)

    def start_game(self):
        # welcome message
        for id in self.client_dict.keys():
            connectionSocket = self.client_dict[id][1]  # socket
            group1 = self.groups["Group 1"]
            group2 = self.groups["Group 2"]
            message = "Welcome to Keyboard Spamming Battle Royale.\n"
            message += "Group 1:\n==\n"
            for team1 in self.group1.keys():
                message += str(team1) + '\n'
            message += "Group 2:\n==\n"
            for team2 in self.group2.keys():
                message += str(team2) + '\n'
            message += "Start pressing keys on your keyboard as fast as you can!!"
            connectionSocket.send(message)
        return time.time()

    def update_counters(self, connection_socket, ip):
        if connection_socket.recv() > 1:
            if self.client_dict[ip][3] == 1:
                self.counters[0] += 1
            else:
                self.counters[1] += 1

    def end_game(self):
        group1 = self.groups["Group 1"]
        group2 = self.groups["Group 2"]
        message = "Game over! \n"
        message += f"Group 1 typed in {self.counters[0]} characters. Group 2 typed in {self.counters[1]} characters.\n"
        if self.counters[0] > self.counters[1]:
            message += "Group 1 wins! \n\n"
            message += "Congratulations to the winners:\n=="
            message += self.groups['Group 1'][0] + "\n"
            message + self.groups['Group 1'][1] + "\n"
        else:
            message += "Group 2 wins! \n\n"
            message += "Congratulations to the winners:\n=="
            message += self.groups['Group 2'][0] + "\n"
            message + self.groups['Group 2'][1] + "\n"
        return message

    def disconnect_client(self):
        message = "Game over, sending out offer requests..."
        print(message)
        # restart the values
        self.client_dict = {}  # Format of {ip: [port, socket, team_name, group_number]}
        self.groups = {'Group 1': [], 'Group 2': []}
        self.counters = [0, 0]  # group1, group2 counters
        self.start_time = 0
        self.startServer()