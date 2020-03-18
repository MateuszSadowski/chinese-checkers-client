import json
import datetime

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
            'pawns': {},
            'next_turn': -1,
            'last_turn': -1,
            'game_finished': False
        }

    def getMyPawns(self):
        player_id = self.game_state['player']['id']
        return self.game_state['pawns'][player_id]

    def getAllPawns(self):
        return self.game_state['pawns']

    def getFieldNeighbours(self, field):
        return self.game_state['board'][field]['neighbours']

    def getPawnInField(self, field):
        return self.game_state['board'][field]['player']

    def isNextTurn(self):
        return self.game_state['next_turn'] != self.game_state['last_turn']

    def isMyTurn(self):
        return self.game_state['next_turn'] == self.game_state['player']['id']

    def isFinished(self):
        return self.game_state['game_finished']

    def connect(self, ip, port):
        self.socketHandler.connect(ip, port)

    def createAndMakeMove(self, oldField, newField):
        move = { 
            'createdAt': datetime.datetime.now().isoformat() + '+00:00',
            'oldFieldID': oldField,
            'newFieldID': newField
        }
        move_msg = json.dumps(move)
        self.socketHandler.send(move_msg)

    def loginAndWaitToStart(self, username, game_id):
        user = {
            'username': username,
            'gameID': game_id
        }

        login_msg = json.dumps(user)
        self.socketHandler.send(login_msg)

        self.receiveAndProcessMessages()

        print('[INFO] Waiting for game to start...\n')
        self.receiveAndProcessMessages()

    def initializeState(self):
        if self.game_state['board'] == {}:
            print('!!ERROR!! Board info not initialized')
            return

        for player in self.game_state['players']:
            player_id = player['id']
            self.game_state['pawns'][player_id] = []
        
        for key, field in self.game_state['board'].items():
            player_id = field['player']
            if player_id is None:
                continue
            self.game_state['pawns'][player_id].append(key)

    def receiveAndProcessMessages(self):
        messages = self.socketHandler.receiveAndSplitMessages()
        if(messages != -1):
            for msg in messages:
                self.game_state = self.messageHandler.handleMessage(msg, self.game_state)