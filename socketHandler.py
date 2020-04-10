import helper
import time
import socket

RECV_LEN = 10000000

SEND_DELAY = 3
EMPTY_RESPONSE_DELAY = 1

class SocketHandler:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('[INFO] Socket successfully created\n')
        except socket.error as err:
            print('!!ERROR!! Socket creation failed with error {0}'.format(err))

    def connect(self):
        try:
            self.socket.connect((self.ip, self.port))
            print('[INFO] Socket successfully connected to {0} on port {1}\n'.format(self.ip, self.port))
        except self.socket.error as err:
            print('!!ERROR!! Socket connection failed with error {0}\n'.format(err))
        
    def close(self):
        try:
            self.socket.close()
            print('[INFO] Socket successfully closed\n')
        except self.socket.error as err:
            print('!!ERROR!! Socket failed to close with error {0}\n'.format(err))

    def receiveAndSplitMessages(self):
        response = self.socket.recv(RECV_LEN)
        if not response:
            print('[INFO] No response from server, check if game ID is correct\n')
            self.close()
            return -1
        response = response.decode()
        messages = response.split('\r\n')
        messages = helper.removeValuesFromList(messages, '')
        return messages

    def send(self, msg):
        # print('[INFO] Sending: ' + msg + '\n')
        time.sleep(SEND_DELAY)
        return self.socket.send(msg.encode())