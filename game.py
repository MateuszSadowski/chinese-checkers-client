import json

import helper
import socketHandler
import messageHandler

class Game:
    def __init__(self):  
        self.socketHandler = socketHandler.SocketHandler()
        self.messageHandler = messageHandler.MessageHandler()
        self.game_state = {
            'player': {},
            'players': [],
            'board': {},
            'next_turn': -1,
            'last_turn': -1
        }

    def connect(self, ip, port):
        self.socketHandler.connect(ip, port)

    def login(self, username, game_id):
        user = {
            'username': username,
            'gameID': game_id
        }

        login_msg = json.dumps(user)
        self.socketHandler.send(login_msg)

        messages = self.socketHandler.receiveAndSplitMessages()
        if(messages != -1):
            for msg in messages:
                self.game_state = self.messageHandler.handleMessage(msg, self.game_state)
