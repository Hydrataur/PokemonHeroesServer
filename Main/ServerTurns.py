import threading
import time

# constants
PORT_NUMBER = 12345  # Port through which clients connect
BUFFER = 1024
NUM_OF_CLIENTS = 3

# global variables
threads = []
lock = threading.Lock()


# Extends Thread class that works with one client
class ServerThread(threading.Thread):

    # overriding of constructor
    def __init__(self, ip, port, socket, client_id, players):
        threading.Thread.__init__(self)
        self.waitToStart = True
        self.socket = socket
        self.ip = ip
        self.port = port
        self.id = client_id
        self.players = players
        self.players.append(self)

    # overriding of Thread run method
    def run(self):
        if self.id == 1:
            resp = "start##0"
            self.send_to_all_clients(resp)
            for item in self.players:
                item.waitToStart = False

        while True:
            buf = self.get_request()
            print("Server got :" + buf)

            if buf == "Bye":
                self.send_to_me("Bye")
                break
            else:
                self.send_to_all_clients(buf)

        self.socket.close()
        print('Closed connection from ip=', self.ip, "port=", self.port)
        self.players.remove(self)
        time.sleep(2)

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

        j = 0  # counter of players in the game
        #  Create list of one couple
        players = []
        # connection loop
        while j < NUM_OF_CLIENTS:
            new_client = server_socket.accept()  # Connected point. Server wait for client
            socket, address = new_client
            ip, port = address

            print("Received connection from ip=:", ip, "port=", port)
            resp = "Wait to start##" + str(j) + "\n"
            socket.send(resp.encode())

            # Start thread:
            current_player_thread = ServerThread(ip, port, socket, j, players)
            threads.append(current_player_thread)

            j = j + 1
        for thread in threads:
            thread.start()  # ServerThread(...) - run constructor, start() - run run() method
        for thread in threads:
            thread.join()
        # In this point the main thread waits for ending of all another threads

        print("All threads are finished")
    except Exception as e:
        print(e.args)
        raise e

    finally:
        server_socket.close()


if __name__ == '__main__':
    main()
