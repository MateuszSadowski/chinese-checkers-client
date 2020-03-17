import helper
import time
import socket

RECV_LEN = 10000000
PORT = 8080
IP = 'localhost'

SEND_DELAY = 1
EMPTY_RESPONSE_DELAY = 1

class SocketHandler:
    def __init__(self):  
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('[INFO] Socket successfully created\n')
        except socket.error as err:
            print('!!ERROR!! Socket creation failed with error {0}'.format(err))

    def connect(self, ip, port):
        try:
            self.socket.connect((ip, port))
            print('[INFO] Socket successfully connected to {0} on port {1}\n'.format(ip, port))
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
        if response == '':
            print('[INFO] Received an empty reponse\n')
            time.sleep(EMPTY_RESPONSE_DELAY)
            return -1
        messages = response.split('\r\n')
        messages = helper.removeValuesFromList(messages, '')
        return messages

    def send(self, msg):
        print('[INFO] Sending: ' + msg + '\n')
        time.sleep(SEND_DELAY)
        return self.socket.send(msg)