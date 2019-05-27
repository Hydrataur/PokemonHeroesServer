import threading
import time

# constants
PORT_NUMBER = 12345  # Port through which clients connect
BUFFER = 1024
NUM_OF_CLIENTS = 3  # Two player clients and Android

# global variables
threads = []


class ServerThread(threading.Thread):
    """
    Extends Thread class that works with one client
    """
    def __init__(self, ip, port, socket, client_id, players):
        """
        Constructor, fields definition
        """
        threading.Thread.__init__(self)
        self.waitToStart = True
        self.socket = socket
        self.ip = ip
        self.port = port
        self.id = client_id
        self.players = players
        self.players.append(self)  # Add self to list of players

    def run(self):
        """"
        Overriding of Thread run method
        Includes implementation of protocol between server/client
        """
        if self.id == 1:
            resp = "start##0"  # Tell client one that they're connected to the server
            self.send_to_all_clients(resp)  # Send the message
            for item in self.players:  # Start players threads
                item.waitToStart = False

        while True:  # Infinite loop until we get an end request from a player
            buf = self.get_request()  # Get the message as a simple String
            print("Server got :" + buf)  # Print what we got (for debugging)

            if buf == "Bye":  # If clients disconnect message will be bye, instructing the end of the process
                self.send_to_me("Bye")  # Send message to self so that it will be handled
                break  # Exit the while loop
            else:
                self.send_to_all_clients(buf)  # If not quitting, send message to all the clients where they will handle it

        self.socket.close()  # While loop has been exited meaning shutdown of server. Close the socket
        print('Closed connection from ip=', self.ip, "port=", self.port)  # Inform of server shutdown
        self.players.remove(self)
        time.sleep(2)  # Pause the thread for two seconds to inform clients of shutdown

    def get_request(self):
        """
        Receive request from client and return it.
        """
        request = self.socket.recv(BUFFER)  # Get message from socket
        request = request.strip()  # remove white chars (TAB, ENTER)
        request_str = request.decode()  # decode by utf-8 standart, convert to string
        return request_str  # Return message once it's been simplified

    def send_to_all_clients(self, response_str):
        """
        Send a message to all the clients connected
        """
        response_str = response_str + "\n"  # Enter in message
        for player_thread in self.players:  # Send to each player separately
            response = response_str.encode()  # Encode the message
            player_thread.socket.send(response)  # Send the message through the socket

    def send_to_me(self, response_str):
        """
        Send message to server for quitting if needed
        """
        response_str = response_str + "\n"  # Enter in message
        response = response_str.encode()  # Encode the message
        self.socket.send(response)  # Send the message through the socket


def main():
    """
    Set up the server:
    create an INET, STREAMing socket
    INET socket - IP protocol based sockets which use IP addresses and ports
    A socket is just an abstraction of a communication end point
    Address Family : AF_INET (this is IP version 4 or IPv4 - 32 bit address - 4 byte address)
    Type : SOCK_STREAM (this means connection oriented TCP protocol)
    Connection means a reliable "stream" of data. The TCP packets have an "order" or "sequence"
    Apart from SOCK_STREAM type of sockets there is another type called SOCK_DGRAM which indicates the UDP protocol.
    Other sockets like UDP , ICMP , ARP dont have a concept of "connection". These are non-connection based
    communication. Which means you keep sending or receiving packets from anybody and everybody.
    """
    import socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Helps the system to forget the server after 1 second
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
            socket, address = new_client  # Get info from our client
            ip, port = address

            print("Received connection from ip=:", ip, "port=", port)  # Inform us of a connected client and their origin
            resp = "Wait to start##" + str(j) + "\n"  # Tell client to wait for now
            socket.send(resp.encode())  # Send the message

            # Start thread:
            current_player_thread = ServerThread(ip, port, socket, j, players)
            threads.append(current_player_thread)

            j = j + 1  # Counter
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
        server_socket.close()  # Close the socket


if __name__ == '__main__':
    """
    Enter main function 
    """
    main()
