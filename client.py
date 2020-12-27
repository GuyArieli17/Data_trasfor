import socket


class Client:
    MAX_TALK_SIZE = 2048

    def __init__(self, server_name, server_ip, server_port):
        self.server_name = server_name
        self.server_port = server_port
        self.server_ip = server_ip

    def broadcast_client(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.listen(13117)  # port 13117 of UDP
        print('Client started, listening for offer request...')
        broadcast_message, server_address = client_socket.recvfrom(self.MAX_TALK_SIZE)
        if broadcast_message["Magic coockie"] == 0xfeedbeef:
            self.server_port = broadcast_message["Server port"]
            self.client_tcp()
            client_socket.close()
        client_socket.close()

    def client_tcp(self):
        clientSocket = socket(socket.AF_INET, socket.SOCK_STREAM)
        counter = 0
        while True:
            clientSocket.connect((self.serverName, self.serverPort))
            message = "I want to send you message"
            clientSocket.send(message)
            receive_message = clientSocket.recv(self.MAX_TALK_SIZE)
            if receive_message == "Type your team name:\n":
                counter += 1
                print(receive_message)
                message = input()
                clientSocket.send(message)
                receive_message = clientSocket.recv(self.MAX_TALK_SIZE)
                if receive_message[:7] == "Welcome":
                    while len(receive_message) == 0: # don't receive a message
                        message = input()
                        clientSocket.send(message)
                    clientSocket.close()
                    self.end_game()

    def end_game(self):
        message = "Server disconnected, listening for offer requests..."
        self.broadcast_client()
