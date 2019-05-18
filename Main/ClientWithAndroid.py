import threading
import time

# constants
PORT_NUMBER = 12345

BUFFER = 1024

#
threads = []


# Extends Thread class that works with one client
class ServerThread(threading.Thread):

    # overriding of constructor
    def __init__(self, ip, port, socket, client_id, players):
        threading.Thread.__init__(self)
        self.waitToStart = True
        self.ask_close = False
        self.socket = socket
        self.ip = ip
        self.port = port
        self.id = client_id
        self.players = players
        self.players.append(self)

    def init_data(self, ip, port, socket, client_id, players):
        print("In init data")
        self.waitToStart = True
        self.ask_close = False
        self.socket = socket
        self.ip = ip
        self.port = port
        self.id = client_id
        self.players = players
        self.players.append(self)
        self.game_on = False
        print("Received connection from ip=:", self.ip, "port=", self.port)
        resp = "Wait to start##" + str(self.id)
        self.send_to_me(resp)
        semaphore.release()

    # overriding of Thread run method
    def run(self):
        print("Received connection from ip=:", self.id, "port=", self.port)
        resp = "Wait to start##" + str(self.id)
        self.send_to_me(resp)

        if self.id == 1:
            resp = "start##0"
            self.send_to_all_clients(resp)
            for item in self.players:
                item.waitToStart = False

        while True:
            buf = self.get_request()
            print("Server got :" + buf)

            if buf == "Bye":
                # may be you want check here if self.waitToStart?...
                self.ask_close = True
                self.send_to_me("Bye")
                if not self.waitToStart:  # the game has been started
                    # need care for opponent
                    break
                else:
                    semaphore.acquire()  # the player cancel wait for opponent
                    # we will use this thread for another player
            else:
                self.send_to_all_clients(buf)

        self.socket.close()
        print('Closed connection from ip=', self.ip, "port=", self.port)
        self.players.remove(self)
        time.sleep(2)
        if id == 0:
            if self.players in list_of_couples:
                list_of_couples.remove(self.players)

    def get_request(self):
        """Receive request from client and return it."""
        request = self.socket.recv(BUFFER)
        # remove white chars (TAB, ENTER)
        request = request.strip()
        # decode by utf-8 standart, convert to string
        request_str = request.decode()
        return request_str

    def send_to_all_clients(self, response_str):
        response_str = response_str + "\n"
        for player_thread in self.players:
            response = response_str.encode()
            lock.acquire()
            player_thread.socket.send(response)
            lock.release()

    def send_to_opponents(self, response_str):
        response_str = response_str + "\n"
        for player_thread in self.players:
            if player_thread.socket != self.socket:
                response = response_str.encode()
                lock.acquire()
                player_thread.socket.send(response)
                lock.release()

    def send_to_me(self, response_str):
        response_str = response_str + "\n"
        response = response_str.encode()
        lock.acquire()
        self.socket.send(response)
        lock.release()


def connection_for_android():
    import socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # bind socket to localhost and  PORT_NUMBER
        server_socket.bind(('', ANDROID_PORT_NUMBER))

        # become a server socket
        server_socket.listen(2)
        print("Server is listening for Android")

        while servers_control_dict["android_loop"]:
            server_socket.settimeout(20)
            android_client = server_socket.accept()  # Connected point. Server wait for client
            print("Connection accepted from Android")
            socket, address = android_client
            print("Got socket and address")
            ip, port = address
            print("Got ip and port")
            print(ip)
            print(port)
            mess = socket.recv(BUFFER)
            print("First mess")
            mess = mess.strip()
            print("After strip")
            mess = mess.decode()
            print("After decode: " + mess)
            [ip1, ip2] = mess.split("##")
            print("mess split")
            for couple in list_of_couples:
                [player1, player2] = couple
                if player1.ip == ip1 and player2.ip == ip2 or player1.ip == ip2 and player2.ip == ip1:
                    print("add new thread to players, add new attribute self.android = True")

    except Exception as e:
        print(e.args)
        raise e

    finally:
        server_socket.close()
        servers_control_dict["android_loop"] = False


def main():
    # Set up the server:

    # create an INET, STREAMing socket
    # INET socket - IP protocol based sockets which use IP addresses and ports
    # A socket is just an abstraction of a communication end point
    import socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Address Family : AF_INET (this is IP version 4 or IPv4 - 32 bit address - 4 byte address)
    # Type : SOCK_STREAM (this means connection oriented TCP protocol)
    # Connection means a reliable "stream" of data. The TCP packets have an "order" or "sequence"
    # Apart from SOCK_STREAM type of sockets there is another type called SOCK_DGRAM which indicates the UDP protocol.
    # Other sockets like UDP , ICMP , ARP dont have a concept of "connection". These are non-connection based
    # communication. Which means you keep sending or receiving packets from anybody and everybody.

    # Helps to system forget server after 1 second
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # bind socket to localhost and  PORT_NUMBER
        server_socket.bind(('', PORT_NUMBER))

        # become a server socket
        server_socket.listen(5)
        print("Server is listening")
        # the argument to listen  - (5) tells the socket library that we want it to queue up
        # as many as 5 connect requests when the program is already busy.
        # the 6th connection request shall be rejected.

        # create connection in another port for androids
        androids_thread = threading.Thread(target=connection_for_android())
        print("after connection for android")
        androids_thread.setDaemon(True)
        print("About to start android thread")
        androids_thread.start()

        print("Android thread started")

        j = 0  # counter of players in couple
        #  Create list of one couple
        players = []
        current_player_thread = None
        print("Before main loop")
        # Have the server serve "forever":
        while servers_control_dict["main_loop"]:
            print("In main loop")
            new_client = server_socket.accept()  # Connected point. Server wait for client
            print("Client found")
            socket, address = new_client
            ip, port = address
            if j == 1 and current_player_thread and current_player_thread.ask_close:
                j = 0
                players.clear()
                current_player_thread.init_data(ip, port, socket, j, players)
            else:
                # Start thread:
                current_player_thread = ServerThread(ip, port, socket, j, players)
                threads.append(current_player_thread)
                current_player_thread.start()  # ServerThread(...) - run constructor, start() - run run() method
            j = j + 1
            if j == 2:
                list_of_couples.append(players)
                j = 0
                players = []

    except Exception as e:
        print(e.args)

    finally:
        server_socket.close()
        servers_control_dict["main_loop"] = False
        servers_control_dict["android_loop"] = False


if __name__ == '__main__':
    main()