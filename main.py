from server import *
from client import *
if __name__ == '__main__':

    mystic_server = server('mystic','127.0.0.1',2000)
    # valor_server = server('mystic','127.0.0.2',2000)
    # mystic_server.startServer()
    # Instinct = client(mystic_server.server_ip,mystic_server.server_port,12)
    Instinct = client(mystic_server.server_ip,mystic_server.server_port)
    # Instinct.start_client()
    #
    # Instinct= Client(mystic_server.server_name,mystic_server.server_ip,mystic_server.server_port)
    # Instinct.start_client()
    #
    # Rocket = Client(mystic_server.server_name,mystic_server.server_ip,mystic_server.server_port)
    # Rocket.start_client()
    #
    # Beitar = Client(mystic_server.server_name,mystic_server.server_ip,mystic_server.server_port)
    # Beitar.start_client()
    #
    # Katamon = Client(mystic_server.server_name,mystic_server.server_ip,mystic_server.server_port)
    # Katamon.start_client()
