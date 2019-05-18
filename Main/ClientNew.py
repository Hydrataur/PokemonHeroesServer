# coding=utf-8
import socket
import threading


class ConnectAndSendThread(threading.Thread):
    def run(self):
        # Connect to the server:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect (('localhost', 12345))
        # Start reading from server in separate thread
        ReadThread(client).start()

        while True :
            # Send some messages:
            request_str = input("Your request")
            request_str = request_str.strip()

            client.send((request_str+"\n").encode())
            if request_str == "exit":
                break


class ReadThread(threading.Thread):

    def __init__(self, client):
        self. client = client
        threading.Thread.__init__(self)

    def run(self):
        while True :
            request = self.client.recv(1024)
            request = request.strip()
            request_str = request.decode()
            print(request_str)
            if request_str == "Bye":
                break
        self.client.close()


def main():
    ConnectAndSendThread().start()


if __name__ == '__main__':
    main()

